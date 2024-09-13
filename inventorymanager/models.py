from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='inventorymanager_users',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='inventorymanager_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )

class Supplier(models.Model):
    name = models.CharField(max_length=140, null = False)
    contact_name = models.CharField(max_length=75)
    contact_email = models.CharField(max_length=75)
    contact_phone = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.name}'

class Category(models.Model):
    name = models.CharField(max_length=140, null = False)
    description = models.CharField(max_length=75)

    def __str__(self):
        return f'{self.name}'
    class Meta:
            verbose_name_plural = "Categories"

class Customer(models.Model):
    first_name = models.CharField(max_length=75, null = False)
    last_name = models.CharField(max_length=75, null = False)
    email = models.CharField(max_length=75)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Product(models.Model):
    name = models.CharField(max_length=140, null = False)
    description = models.CharField(max_length=75)
    unit_cost = models.FloatField(null = False)
    quantity_in_stock = models.IntegerField(null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return f'{self.name}'

class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f'{self.id}'

class OrderItem(models.Model):
    quantity = models.IntegerField(null=False)
    unit_price = models.FloatField(null=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_items")

    def __str__(self):
        return f'Product: {self.product.name}, Order: {self.order.id}'