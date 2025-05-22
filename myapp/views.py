from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
import stripe
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.views.decorators.http import require_POST
from django.conf import settings
from myapp.models import *
from twilio.rest import Client
from django.core.mail import send_mail
from django.utils.encoding import force_str
import uuid 
import random
import base64
from django.core.paginator import Paginator
from random import shuffle




from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings






# def send_sms(to, message):
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER, settings.TWILIO_VERIFY_SERVICE_SID)
#     # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)    
#     message = client.messages.create(
#         body=message,
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=to
#     )

#     return message.sid




class RegisterForm(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return HttpResponse("Passwords do not match")

        subject = 'Verify Your Email'
        token = str(uuid.uuid4())  
        link = f"http://127.0.0.1:8000/verify/?token={token}"  
        message = f'Click the link below to verify your email: {link}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        Verify.objects.create(email=email, token=token)

        user = User(
            name=name,
            username=username,
            email=email,
            phone=phone,
            password=make_password(password1)
        )
        user.save()

        return render(request, 'verify_email.html')
    

class LoginForm(View):
    def get(self, request):
        message = request.GET.get('message', None)  
        return render(request, 'login.html', {"message": message})

    def post(self, request):
        email = request.POST.get('username')  
        password = request.POST.get('password')

        user = User.objects.filter(email=email).first()
        if user and not user.email_verified:
            return HttpResponse("Email not verified")
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            user_id=str(user.id)
            userid = base64.urlsafe_b64encode(user_id.encode()).decode()
            print(f"Encoded User ID: {userid}")
            login(request, user)
            return redirect(f'/home/?user={userid}')
        else:
            return HttpResponse("Invalid credentials")
    
    



class HomePage(View):
    def get(self, request):
        user_id = None
        if request.user.is_authenticated:
            user_id = base64.urlsafe_b64encode(str(request.user.id).encode()).decode()

        search_query = request.GET.get('search', '')
        selected_category = request.GET.get('category', None)
        categories = Products.objects.values_list('category', flat=True).distinct()

        
        products = Products.objects.all()

        if search_query:
            products = products.filter(name__icontains=search_query)

        if selected_category:
            products = products.filter(category__iexact=selected_category)

       
        paginator = Paginator(products, 32)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'home.html', {
            'page_obj': page_obj,
            'user': request.user,
            'encoded_user_id': user_id,
            'categories': categories,
            'selected_category': selected_category,
            'search_query': search_query, 
        })



# class HomePage(View):
#     def get(self, request):
       
#         user_id = None
#         if request.user.is_authenticated:
#             user_id = base64.urlsafe_b64encode(str(request.user.id).encode()).decode()

#         # Get the selected category from the query parameters
#         selected_category = request.GET.get('category', None)

#         # Get all unique categories
#         categories = Products.objects.values_list('category', flat=True).distinct()

#         # If a category is selected, filter products by category, otherwise get all products
#         if selected_category:
#             product = Products.objects.filter(category__iexact=selected_category)
#         else:
#             product = Products.objects.all()

#         # Shuffle the products randomly
#         product_list = list(product)  # Convert queryset to a list
#         random.shuffle(product_list)

#         # Render the template with shuffled products
#         return render(request, 'home.html', {
#             'product': product_list,  # Pass the shuffled products to the template
#             'user': request.user,
#             'encoded_user_id': user_id,
#             'categories': categories,
#             'selected_category': selected_category,
#         })

class DetailPage(View):
    def get(self, request, id, *args, **kwargs):
       
        user_id = request.GET.get('user')
        # user_id = base64.urlsafe_b64decode(user_id).decode()
        # user_id = int(user_id)

        product = Products.objects.filter(id=id).last()
        related_products = list(Products.objects.filter(categoryid=product.categoryid).exclude(id=product.id))  
        shuffle(related_products)  
        related_products = related_products[:4] 
        return render(request, 'detailpage.html', {
            'product': product,
            'user': request.user,  
            'encoded_user_id': user_id, 
            'related_products': related_products,  
        })
    

 


class CartView(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Please login first!"})

        user_id = request.GET.get('user')
        size = request.GET.get('size')  

        if not size:  
            return JsonResponse({"status": "error", "message": "Please select a size!"})

        try:
            user_id = base64.urlsafe_b64decode(user_id).decode()
            user_id = int(user_id)
        except (TypeError, ValueError):
            return JsonResponse({"status": "error", "message": "Invalid user ID!"})

        user = User.objects.filter(id=user_id).last()
        product = get_object_or_404(Products, id=id)

        if not user:
            return JsonResponse({"status": "error", "message": "User not found!"})

        check = Cart.objects.filter(Products=product, user=user, size=size).last()
        if check:
            return JsonResponse({"status": "warning", "message": "Item already in cart with the selected size!"})

        Cart.objects.create(
            Products=product,
            user=user,
            quantity=1,
            total_amount=product.price,
            image=product.image,
            size=size  
        )

        return JsonResponse({"status": "success", "message": "Item added to cart successfully!"})
    
class Remove_cart(View):
    def get(self, request, id):

        user_id = request.user.id  
        user = User.objects.filter(id=user_id).last()
        if not user:
            return JsonResponse({"status": "error", "message": "User not found!"})

       
        print(f"User ID: {user_id}, Cart Item ID: {id}")

        
        cart_item = Cart.objects.filter(id=id, user=user).last()
        if cart_item:
            cart_item.delete()
            return JsonResponse({"status": "success", "message": "Item removed from cart successfully!"})
        else:
            return JsonResponse({"status": "error", "message": "Item not found in cart."})

class CartPageView(View):
    def get(self, request):
        user_id = request.user.id  
        if not user_id:
            return HttpResponse("Invalid User", status=401)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return HttpResponse("User not found", status=404)

        cart_items = Cart.objects.filter(user=user)  
        total_price = sum(item.total_amount for item in cart_items)  

        User_address = Address.objects.filter(user=user).last()
        if User_address:
            address = User_address.user
        else:
            address = None

        return render(request, 'bag.html', {
            'data': cart_items,
            'price': total_price,
            'user': user,
            'address': address,
        })


class AddItem(View):
    def get(self, request):
        user_id = request.GET.get('user')
        user=User.objects.filter(id=user_id).last()
        data= Cart.objects.filter(user=user_id).all()     
         
        amount=0
        for price in data:
            amount=amount+price.total_amount

        return render (request,"bag.html",{"data":data,"price":amount,"user":user_id})
    

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request) 
        return redirect('login')  
    

class MyOrdersView(View):
    def get(self, request):
        user_id = request.GET.get('user')
        user = User.objects.filter(id=user_id).first()
       
        if not user:
            return HttpResponse("Invalid User")

        transactions = Transaction.objects.filter(user_id=user).order_by('-created_at')

        exchange_rate = 86.6 

        orders = []
        for transaction in transactions:
            cart_items = transaction.items.all()
            orders.append({
                'transaction': {
                    'transaction_id': transaction.transaction_id,
                    'total_amount': round(transaction.total_amount * exchange_rate, 2),  
                    'created_at': transaction.created_at,
                },
                'cart_items': cart_items,
                
            })

        return render(request, 'myorders.html', {'orders': orders, 'user': user_id})



#/////////////////////////////////////////////////////////////// payment gateway/////////////////////////////////////////////////////////////////

stripe.api_key = "sk_test_51R10aqBSTAAEIUsJkuRi05oBcyiTBtoTyUjikxCV9kPJDPNTSK5pGnz7A0G3jRvPEASnDOaO7wLBiQebTgUak8ed00IsG8YMpv"
@csrf_exempt
def create_checkout_session(request):
    user_id = request.GET.get('user')
    user = User.objects.filter(id=user_id).last()

    if request.method == "POST":
        try:
            data = json.loads(request.body)  
            cart_total_inr = float(data.get("cart_total", 0))  

            response = requests.get('https://api.exchangerate-api.com/v4/latest/INR')
            exchange_rate = response.json().get('rates', {}).get('USD', 0.012)  

            if not exchange_rate:
                return JsonResponse({'error': 'Unable to fetch exchange rate'}, status=500)

            cart_total_usd = round(cart_total_inr * exchange_rate, 2)  
            cart_total_usd_cents = int(cart_total_usd * 100)  

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=user.email,  
                line_items=[{
                    'price_data': {
                        'currency': 'USD',
                        'product_data': {'name': 'Shopping Cart Items'},
                        'unit_amount': cart_total_usd_cents,  
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success',
                cancel_url='http://127.0.0.1:8000/cancel',
            )

            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        return JsonResponse({'error': f'Invalid payload: {str(e)}'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': f'Invalid signature: {str(e)}'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get("customer_details", {}).get("email", None)

        if email:
            user = User.objects.filter(email=email).first()

            if user:
                cart_items = Cart.objects.filter(user=user)
                if cart_items.exists():
                    cart_instance = cart_items.first()  
                    print(f"Cart instance being passed: {cart_instance}, ID: {cart_instance.id }")

                    transaction = Transaction(
                        user=user,
                        total_amount=session.get("amount_total", 0) / 100,
                        transaction_id=session.get("id", "")
                    )
                    transaction.save()
                   

                    for cart_item in cart_items:
                        item = TransactionCartItem.objects.create(
                            transaction=transaction,
                            product=cart_item.Products,
                            quantity=cart_item.quantity,
                            total_price=cart_item.total_amount
                        )
                        print(f"Created TransactionCartItem: {item.id}")

                        cart_items.delete()  
                        print("Cleared cart items but kept the cart instance")

                                            # Get user's address
                        cum_address = Address.objects.filter(user=user.id).last()

                        if cum_address:
                            subject = 'Invoice for Your Order'
                            from_email = settings.EMAIL_HOST_USER
                            recipient_list = [email]

                            # Prepare context for invoice template
                            context = {
                                'user': user,
                                'email': email,
                                'address': cum_address,
                                'transaction': transaction,
                            }

                            # Render invoice HTML from template
                            html_content = render_to_string('invoice.html', context)

                            # Send email with HTML content
                            email_message = EmailMultiAlternatives(subject, '', from_email, recipient_list)
                            email_message.attach_alternative(html_content, "text/html")
                            email_message.send()

                    print(f"Transaction {transaction.id} created successfully with cart items!")
                else:
                    print("No cart items found for the user.")
            else:
                print("User not found.")
        else:
            print("Email not found in the session.")

    return JsonResponse({'message': 'Event received'}, status=200)


def payment_success(request):
    return render (request , "success.html")


def payment_cancel(request):
    return render(request, "cancel.html")






class WishlistView(View):
    def get(self, request):
        user_id = request.GET.get('user') or request.user.id 
        
        user_id = base64.urlsafe_b64decode(user_id).decode()
        user_id = int(user_id)
        wishlist_items = WishlistItem.objects.filter(user=user_id).all()
        wish_list = []
        for i in wishlist_items:
            data = { 
                "id": i.id,
                "user": i.user.id, 
                "image": i.product.image.url if i.product.image else None,
                "product": i.product,
                "created_at": i.created_at
            }
            wish_list.append(data)
        
        return render(request, 'wishlist.html', {'wishlist_items': wish_list})
    


class RemoveFromWishlistView(View):
    def post(self, request, item_id):
        wishlist_item = get_object_or_404(WishlistItem, id=item_id)
        wishlist_item.delete()
        return JsonResponse({"status": "success", "message": "Item removed from wishlist successfully!"})


class MoveToCartView(View):
    def post(self, request, item_id):
        wishlist_item = get_object_or_404(WishlistItem, id=item_id)
        Cart.objects.create(
            user=wishlist_item.user,
            Products=wishlist_item.product,
            quantity=1,
            total_amount=wishlist_item.product.price,
            image=wishlist_item.product.image
        )
        wishlist_item.delete()
        return JsonResponse({"status": "success", "message": "Item moved to cart successfully!"})


# class RemoveFromWishlistView(View):
#     def post(self, request, item_id):
#         wishlist_item = get_object_or_404(WishlistItem, id=item_id)
#         wishlist_item.delete()
#         return redirect('wishlist') 

# class MoveToCartView(View):
#     def post(self, request, item_id):
#         wishlist_item = get_object_or_404(WishlistItem, id=item_id)
       
#         Cart.objects.create(
#             user=wishlist_item.user,
#             Products=wishlist_item.product, 
#             quantity=1,
#             total_amount=wishlist_item.product.price,
#             image=wishlist_item.product.imageD
#         )
        
        wishlist_item.delete()
        return redirect('wishlist')  
    


class AddToWishlistView(View):
    def get(self, request, product_id):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Please login first!"})

        user_id = request.GET.get('user')
        user_id = base64.urlsafe_b64decode(user_id).decode()
        user_id = int(user_id)
        user = User.objects.filter(id=user_id).first()
        product = get_object_or_404(Products, id=product_id)

        if not user:
            return JsonResponse({"status": "error", "message": "User not found!"})

        existing_item = WishlistItem.objects.filter(user=user, product=product).first()
        if existing_item:
            return JsonResponse({"status": "warning", "message": "Item already in wishlist!"})

        WishlistItem.objects.create(user=user, product=product, image=product.image)
        return JsonResponse({"status": "success", "message": "Item added to wishlist successfully!"})
    

class VerifyEmailView(View):
    def get(self, request):
        user_token = request.GET.get('token')
       
        user = Verify.objects.filter(token=user_token).last()
       
        if user:
            user = User.objects.filter(email=user.email).last()
            user.email_verified = True
            user.save()
            return redirect('/')
        else:
            return JsonResponse({"status": "error", "message": "User not found!"}, status=404)


class MyProfileView(View):
    def get(self, request):
        user_id = request.GET.get('user')
         
        user_id = base64.urlsafe_b64decode(user_id).decode()
        user_id = int(user_id)
        user = User.objects.filter(id=user_id).first()

        if not user:
            return HttpResponse("Invalid User")

        return render(request, 'my_profile.html', {'user': user})

class OTPVerificationView(View):
    def get(self, request):
        return render(request, 'otp_verification.html')

    def post(self, request):
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        user_id = request.session.get('user_id')

        if str(entered_otp) == str(session_otp):
            user = User.objects.filter(id=user_id).first()
            if user:
                user.phone_verified = True
                user.save()
                del request.session['otp']  
                return redirect(f'/home/?user={user.id}') 
        return HttpResponse("Invalid OTP. Please try again.")
    

class VerifyPhoneView(View):
    def get(self, request):
        user_id = request.GET.get('user')
        user = User.objects.filter(id=user_id).first()

        if not user or not user.phone:
            return HttpResponse("Invalid User or Phone Number")

        
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp  
        request.session['user_id'] = user.id

        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your OTP for phone verification is {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone
        )

        print(f"OTP sent to {user.phone}: {otp}") 
        return redirect('otp_verification')
    


class SearchProductsView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        products = Products.objects.filter(
name__icontains
=query)  # Search by product name
        return render(request, 
'search_results.html'
, {'products': products, 'query': query})





class MenView(View):
    def get(self, request):
        # Fetch men's products
        products = Products.objects.filter(category__in=['1', '2', '3', '8'])  
        return render(request, 'men.html', {'products': products})




class MenShirtsView(View):
    def get(self, request):
        # Fetch men's shirts
        products = Products.objects.filter(categoryid='1')  
        print(f"Men's Shirts Products: {products}")  
        return render(request, 'men_shirts.html', {'products': products})

class MenPoloView(View):
    def get(self, request):
        # Fetch men's polos
        products = Products.objects.filter(categoryid='2') 
        print(f"Men's Polos Products: {products}")  
        return render(request, 'men_polos.html', {'products': products})

class MenBottomwearView(View):
    def get(self, request):
        # Fetch men's bottomwear
        products = Products.objects.filter(categoryid='3')  
        print(f"Men's Bottomwear Products: {products}")  
        return render(request, 'men_bottomwear.html', {'products': products})
    

class MenPoloView(View):
    def get(self, request):
        # Fetch men's polos
        products = Products.objects.filter(categoryid='2')  
        return render(request, 'men_polos.html', {'products': products})


class MenBottomwearView(View):
    def get(self, request):
        # Fetch men's bottomwear
        products = Products.objects.filter(categoryid='3')  
        return render(request, 'men_bottomwear.html', {'products': products})
    
class MenTopwearView(View):
    def get(self, request):
        products = Products.objects.filter(categoryid='8')  
        return render(request, 'men_topwear.html', {'products': products})

    


class WomenView(View):
    def get(self, request):
        # Fetch women's products
        products = Products.objects.filter(category__in=['4', '5']) 
        return render(request, 'women.html', {'products': products})
    


class WomenTopwearView(View):
    def get(self, request):
        # Fetch women's topwear
        products = Products.objects.filter(categoryid='4') 
        return render(request, 'women_topwear.html', {'products': products})
    


class WomenBottomwearView(View):
    def get(self, request):
        # Fetch women's bottomwear
        products = Products.objects.filter(categoryid='5')  
        return render(request, 'women_bottomwear.html', {'products': products})
    



class AccessoriesView(View):
    def get(self, request):
        # Fetch accessories
        products = Products.objects.filter(category__in=['6', '7', '9'])  
        return render(request, 'accessories.html', {'products': products})
    


class AccessoriesBeltsView(View):
    def get(self, request):
        # Fetch belts
        products = Products.objects.filter(categoryid='7')  
        return render(request, 'accessories_belts.html', {'products': products})
    


class AccessoriesSocksView(View):
    def get(self, request):
        # Fetch socks
        products = Products.objects.filter(categoryid='6')  
        return render(request, 'accessories_socks.html', {'products': products})

class AccessoriesTiesView(View):
    def get(self, request):
        products = Products.objects.filter(categoryid='9') 
        return render(request, 'accessories_ties.html', {'products': products})
    

class UserAddress(View):
    def get(self, request):
        return render(request, 'address.html')

    def post(self, request):
        # user_id = request.GET.get('user')
        user_id = request.user.id
        user_id = User.objects.filter(id=user_id).last()

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        addaddress = Address.objects.create(
            user=user_id,
            name=name,
            phone=phone,
            address=address,
            city=city,
            country=country,
            state=state,
            pincode=pincode
        )
        # user = User.objects.filter(id=user_id).last()
        return redirect('cart_page')

































