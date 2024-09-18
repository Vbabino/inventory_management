from django.forms import inlineformset_factory
from django import forms
from .models import *

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(SupplierForm, self).__init__(*args, **kwargs)
        # Set specific fields as not required
        self.fields['contact_name'].required = False
        self.fields['contact_email'].required = False
        self.fields['contact_phone'].required = False

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        # Set specific fields as not required
        self.fields['email'].required = False
        self.fields['phone'].required = False

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean_unit_cost(self):
        unit_cost = self.cleaned_data.get('unit_cost')
        if unit_cost is not None and unit_cost < 0:
            raise forms.ValidationError('Unit cost must be greater than or equal to zero')
        return unit_cost

    def clean_quantity_in_stock(self):
        quantity_in_stock = self.cleaned_data.get('quantity_in_stock')
        if quantity_in_stock is not None and quantity_in_stock < 0:
            raise forms.ValidationError('Quantity in stock must be greater than or equal to zero')
        return quantity_in_stock

    
class OrderForm(forms.ModelForm):
    class Meta:
        model =  Order
        fields = ['customer']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is not None and unit_price < 0:
            raise forms.ValidationError('Unit price must be greater than or equal to zero')
        return unit_price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError('Quantity in stock must be greater than or equal to zero')
        return quantity


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
