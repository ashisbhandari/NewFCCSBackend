
from . import views
from django.urls import path, include

urlpatterns = [
    path('add/', views.add_Product, name='add_product'),
    path('view/', views.View_Product, name='view_product'),
    path('view/<str:product_id>/', views.product_by_id, name='product_by_id'),
    path('tracking/<str:product_id>/', views.add_tracking_update, name='add_tracking_update'),
    path('tracking/view/<str:identifier>/', views.view_tracking_history, name='view_tracking_history'),
]
