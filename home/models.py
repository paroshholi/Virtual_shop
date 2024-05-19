from django.db import models
from django.contrib.auth.models import User

class OrderHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='OrderedProduct')
    total_price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    date_ordered = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.pk} - {self.customer.username}"

class OrderedProduct(models.Model):
    order_history = models.ForeignKey(OrderHistory, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"
# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('mobile', 'Mobiles'),
        ('laptop', 'Laptops'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='product_images/')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name

    
class Order(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        # Add more status options as needed
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    history = models.ForeignKey(OrderHistory, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Order {self.pk} - {self.customer.username}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    @property
    def total_price(self):
        return self.product.price * self.quantity
    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"
class Wishlist(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='home_user_profile')


    def __str__(self):
        return self.user.username
