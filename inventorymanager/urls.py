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




]