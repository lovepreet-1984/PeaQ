from django.urls import path
from django.shortcuts import render, redirect
from .views import *
from . import views
from .views import RemoveFromWishlistView, MoveToCartView, MyProfileView, CartPageView

urlpatterns = [
    
    path('', lambda request: redirect('home'), name='root'),

    
    path('register/', RegisterForm.as_view(), name='register'),
    path('login/', LoginForm.as_view(), name='login'),
    path('home/', HomePage.as_view(), name='home'),
    path('product/<int:id>/', DetailPage.as_view(), name='detail_page'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('product_cart/<int:id>/', CartView.as_view(), name='add_to_cart'),
    path('bag/', CartPageView.as_view(), name='cart_page'),
    path("remove_cart/<int:id>/", Remove_cart.as_view(), name="remove_cart"),
    path('add_item/', AddItem.as_view(), name='view_item'),
    path('checkout/', lambda request: render(request, 'bag.html'), name='checkout'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('success/', payment_success, name="success"),
    path('cancel/', payment_cancel, name="cancel"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
    path('my_orders/', MyOrdersView.as_view(), name='my_orders'),
    path('wishlist/remove/<int:item_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('wishlist/move_to_cart/<int:item_id>/', MoveToCartView.as_view(), name='move_to_cart'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('product_wishlist/<int:product_id>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('verify/', VerifyEmailView.as_view(), name='verify_email'),
    path('my_profile/', MyProfileView.as_view(), name='my_profile'),
    path('otp_verification/', OTPVerificationView.as_view(), name='otp_verification'),
    path('verify_phone/', VerifyPhoneView.as_view(), name='verify_phone'),
    path('men/', MenView.as_view(), name='men'),
    path('men/shirts/', MenShirtsView.as_view(), name='men_shirts'),
    path('men/polos/', MenPoloView.as_view(), name='men_polos'),
    path('men/bottomwear/', MenBottomwearView.as_view(), name='men_bottomwear'),
    path('men/topwear/', MenTopwearView.as_view(), name='men_topwear'),
    path('women/', WomenView.as_view(), name='women'),
    path('women/topwear/', WomenTopwearView.as_view(), name='women_topwear'),
    path('women/bottomwear/', WomenBottomwearView.as_view(), name='women_bottomwear'),
    path('accessories/', AccessoriesView.as_view(), name='accessories'),
    path('accessories/belts/', AccessoriesBeltsView.as_view(), name='accessories_belts'),
    path('accessories/socks/', AccessoriesSocksView.as_view(), name='accessories_socks'),
    path('accessories/ties/', AccessoriesTiesView.as_view(), name='accessories_ties'),
    path('add_address/', UserAddress.as_view(), name='Add_address'),
    
    
    
    
]