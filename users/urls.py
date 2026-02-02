
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('add/', views.add_user, name='add_user'),
    path('user-login/', views.user_login, name='user_login'),#user login url
    path('users-details/',views.user_details, name='users_details'),#users details for test
    path('user-details/<int:user_id>/', views.get_user_details, name='user_profile'),#user profile view and update
    
]
