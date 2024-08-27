from django.db import models
from django.contrib.auth.models import User
from shortuuid.django_fields import ShortUUIDField


class Profile(models.Model):
    """profile"""
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images', blank=True)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Category(models.Model):
    """Categories table"""
    id = ShortUUIDField(primary_key=True, unique=True, length=10, max_length=20, alphabet="abcdef123456")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    """Products table"""
    id = ShortUUIDField(primary_key=True, unique=True, length=10, max_length=20, alphabet="abcdef123456")
    name = models.CharField(max_length=100)
    price = models.IntegerField(max_length=100)
    Original = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    discount = models.IntegerField(default=0)
    is_accessory = models.BooleanField(default=False)
    brand = models.CharField(max_length=100)
    features = models.JSONField(default=dict, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    thumbnail_1 = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    thumbnail_2 = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    thumbnail_3 = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.name

class OfferProduct(Product):
    """Special offer products table"""
    description = models.CharField(max_length=100)
    period = models.CharField(max_length=100)

class PickOfTheWeek(Product):
    """Pick of the week table"""
    major_info = models.CharField(max_length=100)
    more_info = models.CharField(max_length=100)
    added_info = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Pick of the week"
        verbose_name_plural = "Pick of the week"

class Laptop(Product):
    """Laptops table"""
    elements = models.CharField(max_length=100)
    storage = models.CharField(max_length=100)
    added_info = models.CharField(max_length=100)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
    
class Order(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    shippingoption = models.CharField(max_length=100)
    total_amount = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.firstname} {self.lastname}"

class OrderItems(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "OrderItems"
        verbose_name_plural = "OrderItems"
    

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"