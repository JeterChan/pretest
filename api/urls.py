from django.contrib import admin
from django.urls import path
from api.views import import_order, create_products, get_products

urlpatterns = [
    path('import-order/', import_order),
    path('create-products/', create_products),
    path('products/', get_products)
]