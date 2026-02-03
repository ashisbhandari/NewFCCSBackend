
from . import views
from django.urls import path, include

urlpatterns = [
    path('add/', views.add_Product, name='add_product'),
    path('view/', views.View_Product, name='view_product'),
    path('view/<int:product_id>/', views.product_by_id, name='product_by_id'),
    
]
