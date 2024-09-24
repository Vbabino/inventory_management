from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    order_date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f'{self.id}'

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_items")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Creating a new order item, check if there's enough stock
            if self.product.quantity_in_stock < self.quantity:
                raise ValidationError(f'Cannot order more than available stock ({self.product.quantity_in_stock} units left)')
            self.product.quantity_in_stock -= self.quantity
        else:
            self.product.quantity_in_stock -= self.quantity

        # Save the product with the updated quantity_in_stock
        self.product.save()
        
        # Call the original save method to save the OrderItem
        super(OrderItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # When an order item is deleted, add the quantity back to the product's stock
        self.product.quantity_in_stock += self.quantity
        self.product.save()
        super(OrderItem, self).delete(*args, **kwargs)

    def __str__(self):
        return f"OrderItem for product {self.product.name} with quantity {self.quantity}"


