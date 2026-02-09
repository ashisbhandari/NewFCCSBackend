
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_manifest, name='add_manifest'),
    path('view/', views.view_manifests, name='view_manifests'),
    path('update-status/<str:manifest_no>/', views.update_manifest_status, name='update_manifest_status'),
    path('update-manifest/<str:manifest_no>/', views.update_manifest, name='update_manifest'),
    
    path('view-manifest-cns/<str:manifest_no>/', views.view_manifest_cn_numbers, name='view_manifest_cn_numbers'),
    
    
]
