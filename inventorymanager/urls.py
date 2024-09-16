from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("suppliers", views.supplier_view, name="suppliers"),
    path("create_supplier", views.create_supplier, name="create_supplier"),
    path("customers", views.customer_view, name="customers"),
    path("create_customer", views.create_customer, name="create_customer"),
    path("products", views.product_view, name="products"),
    path("create_product", views.create_product, name="create_product"),
    path("orders", views.order_view, name="orders"),
    path("create_order", views.create_order, name="create_order"),
    path("categories", views.category_view, name="categories"),
    path("create_category", views.create_category, name="create_category"),
    # Detail urls
    path('supplier/<int:id>/', views.supplier_detail, name='supplier_detail'),
    path('customer/<int:id>/', views.customer_detail, name='customer_detail'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path('category/<int:id>/', views.category_detail, name='category_detail'),
    # Edit urls
    path('edit_supplier/<int:id>', views.edit_supplier, name='edit_supplier'),
    path('edit_customer/<int:id>', views.edit_customer, name='edit_customer'),


    # Delete urls
    path('delete_supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),
    path('delete_customer/<int:id>/', views.delete_customer, name='delete_customer'),









]