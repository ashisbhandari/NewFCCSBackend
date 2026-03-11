
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='home_page '),
    path('add/', views.add_user, name='add_user'),
    path('user-login/', views.user_login, name='user_login'),#user login url
    path('view/',views.all_user, name='view'),#view all users by admin
    path('user-details/<str:user_id>/', views.get_user_details, name='user_profile'),#user profile view and update
    
]
