from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from .forms import *

def index(request):
    # Authenticated users view the Dashboard
    if request.user.is_authenticated:
        return render(request, "inventorymanager/index.html", {})
    else:
        return redirect("login")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "inventorymanager/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "inventorymanager/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def create_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("suppliers")

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm()
    
    return render(request, 'inventorymanager/createSupplier.html', {'form': form})

@login_required
def supplier_view(request):
    suppliers = Supplier.objects.all()
    
    return render(request, 'inventorymanager/suppliers.html', {
            "suppliers": suppliers
        })

@login_required
def customer_view(request):
    customers = Customer.objects.all()

    return render(request, 'inventorymanager/customers.html', {
            "customers": customers
        })

@login_required
def create_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customers")
        
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerForm()
    
    return render(request, 'inventorymanager/createCustomer.html', {'form': form})

@login_required
def product_view(request):
    products = Product.objects.all()
    
    return render(request, 'inventorymanager/products.html', {
            "products": products,
            
        })

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("products")

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    return render(request, 'inventorymanager/createProduct.html', {'form': form})
    
@login_required
def order_view(request):
    orders = Order.objects.all()
    return render(request, 'inventorymanager/orders.html', {
            "orders": orders
        })

@login_required
def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        order_item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and order_item_formset.is_valid():
            order = order_form.save()  
            order_items = order_item_formset.save(commit=False)  # Don't commit to DB yet

            # Link each OrderItem to the newly created Order
            for item in order_items:
                item.order = order
                item.save()

            return redirect('orders')  
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        order_form = OrderForm()
        order_item_formset = OrderItemFormSet()

    return render(request, 'inventorymanager/createOrder.html', {
        'order_form': order_form,
        'order_item_formset': order_item_formset,
    })

@login_required
def category_view(request):
    categories = Category.objects.all()
    return render(request, 'inventorymanager/categories.html', {
            "categories": categories
        })

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("categories")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    return render(request, 'inventorymanager/createCategory.html', {'form': form})

@login_required
def supplier_detail(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    return render(request, 'inventorymanager/supplier_detail.html', {'supplier': supplier})

@login_required
def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'inventorymanager/customer_detail.html', {'customer': customer})

@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    form = ProductForm(instance=product)
    return render(request, 'inventorymanager/product_detail.html', {'product': product, 'form': form})

@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    orderItem = get_object_or_404(OrderItem, id=id)
    return render(request, 'inventorymanager/order_detail.html', {
        'order': order,
        'orderItem': orderItem
        })

@login_required
def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    return render(request, 'inventorymanager/category_detail.html', {'category': category})

def edit_supplier(request,id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_suppl = get_object_or_404(Supplier, id=id)
        edit_suppl.name = data["name"]
        edit_suppl.contact_name = data["contact_name"]
        edit_suppl.contact_email = data["contact_email"]
        edit_suppl.contact_phone = data["contact_phone"]
        edit_suppl.save()
        return JsonResponse({
            "message": "changes successfully made",
            "name": edit_suppl.name,  # Return the updated supplier details
            "contact_name": edit_suppl.contact_name,
            "contact_email": edit_suppl.contact_email,
            "contact_phone": edit_suppl.contact_phone,
        })
    
def edit_customer(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_cust =get_object_or_404(Customer, id=id)
        edit_cust.first_name = data["first_name"]
        edit_cust.last_name = data["last_name"]
        edit_cust.email = data["email"]
        edit_cust.phone = data['phone']
        edit_cust.save()
        return JsonResponse({
            "first_name": edit_cust.first_name,
            "last_name": edit_cust.last_name,
            "email": edit_cust.email,
            "phone": edit_cust.phone,
        })

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save()
            # return redirect('product_detail', id=updated_product.id)
            return JsonResponse({
                'success': True,
                "name": updated_product.name,
                "description": updated_product.description,
                "unit_cost": updated_product.unit_cost,
                "quantity_in_stock": updated_product.quantity_in_stock,
                "category": updated_product.category.name,
                "supplier": updated_product.supplier.name,
    
        })
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventorymanager/product_detail.html', {'form': form})

 
def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    supplier.delete()
    messages.success(request, 'Supplier deleted successfully')
    return redirect('suppliers')  

def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    messages.success(request, 'Customer deleted successfully')
    return redirect('customers')  

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect('products') 