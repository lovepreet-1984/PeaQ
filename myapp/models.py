from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)  
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=False, null=False)  
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, default=None, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username'] 

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):  
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

AUTH_USER_MODEL = 'myapp.User'




class Products(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=180)  
    price = models.IntegerField()
    image = models.ImageField(upload_to='images/',max_length=500)
    category = models.CharField(max_length=255, default='uncategorized')
    details = models.CharField(max_length=255, default='uncategorized')
    categoryid = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Products = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='images/',max_length=500)
    total_amount = models.IntegerField()
    size = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

    def clear_items(self):
        Cart.objects.filter(id=self.id).delete()
    
class Transaction(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    transaction_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

class TransactionCartItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.IntegerField()

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'


class WishlistItem(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(max_length=500)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'WishlistItem: {self.product.name} for {self.user.email}'
    



class Verify(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'VerifyEmail: {self.email}'


class Address(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Address: {self.user.email}'
    






