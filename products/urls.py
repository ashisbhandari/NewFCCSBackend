
from . import views
from django.urls import path, include

urlpatterns = [
    path('add/', views.add_Product, name='add_product'),
    path('view/', views.View_Product, name='view_product'),
    
]
