
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('add/', views.add_user, name='add_user'),
    
]
