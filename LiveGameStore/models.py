import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY = (
        ('Laptop', 'Laptop'),
        ('PC Case', 'PC Case'),
        ('Keyboard', 'Keyboard'),
        ('Mouse', 'Mouse'),
        ('Monitor', 'Monitor'),
        ('Motherboard','Motherboard'),
        ('Graphics Card','Graphics Card')
    )

    name = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.IntegerField(default=1)
    category = models.CharField(max_length=200, choices=CATEGORY)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Allow nulls if needed
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(null=True, blank=True)
    date = models.DateField(default=datetime.datetime.today)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.product.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return self.user.username