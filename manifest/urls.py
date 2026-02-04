
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_manifest, name='add_manifest'),
    
]
