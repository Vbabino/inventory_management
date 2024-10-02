from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from .forms import *
from django.db.models import Sum, F
import json

def index(request):
    # Authenticated users view the Dashboard
    if request.user.is_authenticated:
        low_stock = Product.objects.filter(quantity_in_stock__lte=3)
        
        orders_total = OrderItem.objects.annotate(
                        total_price=F('quantity') * F('unit_price')  
                    ).aggregate(sum_total=Sum('total_price'))['sum_total']
        
        product_total_cost = OrderItem.objects.annotate(
                cost_calculation=F('quantity') * F('product__unit_cost')  
            ).aggregate(total_cost_sum=Sum('cost_calculation'))['total_cost_sum']
        
        net_revenue = float(orders_total) - float(product_total_cost)
        # Sales chart
        sales_data = (OrderItem.objects
                        .values('order__order_date__month')  
                        .annotate(total_revenue=F('quantity') * F('unit_price'))
                        .order_by('order__order_date__month')
                        )

        sales_rev_labels = [f'Month {item["order__order_date__month"]}' for item in sales_data]
        sales_rev_data = [float(item["total_revenue"]) for item in sales_data]
        
        # Top Selling Products Chart
        top_selling_products = (OrderItem.objects
                                .values('product__name')
                                .annotate(total_quantity_sold=Sum('quantity'))
                                .order_by('-total_quantity_sold')[:3]
                                )
        tps_chart_labels = [item['product__name'] for item in top_selling_products]
        tps_chart_data = [item['total_quantity_sold'] for item in top_selling_products]
        
        # Inventory levels Chart
        inventory_levels = (Product.objects
                            .values('name')
                            .annotate(total_qty_in_stock = Sum('quantity_in_stock'))
                            .order_by('-total_qty_in_stock')
                            )
        
        il_chart_labels = [item['name'] for item in inventory_levels]
        il_chart_data = [item['total_qty_in_stock'] for item in inventory_levels]

        # Supplier Contribution Chart

        supplier_contributions = (Product.objects
                                    .values('supplier__name')  
                                    .annotate(total_quantity=Sum('quantity_in_stock'))  
                                    .order_by('-total_quantity')  
                                )
        
        total_inventory = Product.objects.aggregate(total_quantity=Sum('quantity_in_stock'))['total_quantity']
        sc_chart_labels = [item['supplier__name'] for item in supplier_contributions]
        sc_chart_data = [ round((item['total_quantity'] / total_inventory) * 100, 2) if total_inventory else 0 for item in supplier_contributions]
        
        # Customer Orders Analysis

        customer_orders = (OrderItem.objects
                            .values('order__customer__first_name', 'order__customer__last_name')  
                            .annotate(total_spending=Sum(F('quantity') * F('unit_price')))  
                            .order_by('-total_spending')[:3]  
                        )
        
        
        customer_orders_labels = [f"{item['order__customer__first_name']} {item['order__customer__last_name']}" for item in customer_orders]
        customer_orders_data = [float(item['total_spending']) for item in customer_orders]

        context = {
            "low_stock": low_stock.count(),
            "products_total": product_total_cost,
            'orders_total': orders_total,
            'revenue': net_revenue,
            'sales_rev_labels': json.dumps(sales_rev_labels) if sales_rev_labels else json.dumps([]),  
            'sales_rev_data': json.dumps(sales_rev_data) if sales_rev_data else json.dumps([]),
            'tps_chart_labes': json.dumps(tps_chart_labels) if tps_chart_labels else json.dumps([]),
            'tps_chart_data': json.dumps(tps_chart_data) if tps_chart_data else json.dumps([]),
            'il_chart_labels': json.dumps(il_chart_labels) if il_chart_labels else json.dumps([]),
            'il_chart_data': json.dumps(il_chart_data) if il_chart_data else json.dumps([]),
            'sc_chart_labels': json.dumps(sc_chart_labels) if sc_chart_labels else json.dumps([]),
            'sc_chart_data': json.dumps(sc_chart_data) if sc_chart_data else json.dumps([]),
            'customer_orders_labels': json.dumps(customer_orders_labels) if customer_orders_labels else json.dumps([]),
            'customer_orders_data': json.dumps(customer_orders_data) if customer_orders_data else json.dumps([]),

            }

        return render(request, "inventorymanager/index.html", context)
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
            messages.success(request, 'Supplier created successfully')
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
            messages.success(request, 'Customer created successfully')
            return redirect("customers")
        
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerForm()
    
    return render(request, 'inventorymanager/createCustomer.html', {'form': form})

@login_required
def product_view(request):
    products = Product.objects.annotate(
        total_value=Sum(F('quantity_in_stock') * F('unit_cost'))
    )
    low_stock = Product.objects.filter(quantity_in_stock__lte=3)

    if low_stock.count() > 0:
        if low_stock.count() > 1:
            messages.error(request, f'{low_stock.count()} items have low stock')
        else:
            messages.error(request, f'{low_stock.count()} item has low stock')

    return render(request, 'inventorymanager/products.html', {
            "products": products,
            
        })

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully')
            return redirect("products")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    return render(request, 'inventorymanager/createProduct.html', {'form': form})
    
@login_required
def order_view(request):
    orders = Order.objects.annotate(
        total_value=Sum(F('order_items__quantity') * F('order_items__unit_price'))
    )
    
    return render(request, 'inventorymanager/orders.html', {
            "orders": orders
        })



@login_required
def create_order(request):
    
    OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, can_delete=False)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        order_item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and order_item_formset.is_valid():
            order = order_form.save()
            order_items = order_item_formset.save(commit=False)

            # Link each OrderItem to the newly created Order
            for item in order_items:
                item.order = order
                item.save()
            messages.success(request, 'Order created successfully')
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
            messages.success(request, 'Category created successfully')
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
    orderItem = OrderItem.objects.filter(order=order)
    order_form = OrderForm(instance=order)
    OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=0, can_delete=False)
    formset = OrderItemFormSet(instance=order)
    return render(request, 'inventorymanager/order_detail.html', {
        'order': order,
        'orderItem': orderItem,
        'order_form': order_form,
        'formset': formset,
        })

@login_required
def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryForm(instance=category)
    return render(request, 'inventorymanager/category_detail.html', {'category': category, 'form': form})

@login_required
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

@login_required
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
    
@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save()
            
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



@login_required
def cancel_order_update(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == "GET":
        for order_item in order.order_items.all():
            # Restoring current quantity in stock
            order_item.product.quantity_in_stock -= order_item.quantity
            order_item.product.save()
    
    return redirect('orders')
    
@login_required
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            updated_category = form.save()

            return JsonResponse({
                'success': True,
                'name': updated_category.name,
                'description': updated_category.description

            })
    else:
        form = CategoryForm(instance=category)
        return render(request, 'inventorymanager/category_detail.html', {'form': form})

@login_required
def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    supplier.delete()
    messages.success(request, 'Supplier deleted successfully')
    return redirect('suppliers')  

@login_required
def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    messages.success(request, 'Customer deleted successfully')
    return redirect('customers')  

@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect('products') 

@login_required
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    
    for order_item in order.order_items.all():
        order_item.delete()
    
    order.delete()
    messages.success(request, 'Order deleted successfully')
    return redirect('orders') 

@login_required
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, 'Category deleted successfully')
    return redirect('categories')

