from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from .serializers import get_tokens_for_user
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

# default user function view
def user_dashboard(request):
    data = {
        "message": "hello user page is active",
        "status": "success",
        "user": "dashboard_user"
    }
    return JsonResponse(data)



# admin task in user app
# *------------------------------------------------------------*
# add user by admin
@csrf_exempt
@permission_classes([IsAdminUser])
def add_user(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            
            # Create new user
            contact1 = data.get('contact1')
            # password = data.get('password', contact1)  # Use provided password or contact1 as fallback
            user = User.objects.create(
                companyName=data.get('companyName'),
                ownerName=data.get('ownerName'),
                email=data.get('email'),
                country=data.get('country'),
                zipcode=data.get('zipcode'),
                state=data.get('state'),
                city=data.get('city'),
                address1=data.get('address1'),
                address2=data.get('address2', ''),
                contact1=contact1,
                contact2=data.get('contact2', ''),
                password=contact1,  # Set password to contact1
                is_staff=False  # Always set to False when adding users
            )
            user.set_password(contact1)  # Hash the password
            user.save()
            return JsonResponse({
                'status': 'success',
                'message': 'User created successfully',
                'userID': user.userID,
                'ownerName': user.ownerName
            }, status=201)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method is allowed'
    }, status=405)
    
       # helps to get all user data  by admin only 
@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_user(request):
    # Get all users from database
    users = User.objects.all()
    
    users_list = []
    for user in users:
        user_data = {
            'userID': user.userID,
            'companyName': user.companyName,
            'ownerName': user.ownerName,
            'email': user.email,
            'country': user.country,
            'zipcode': user.zipcode,
            'state': user.state,
            'city': user.city,
            'address1': user.address1,
            'address2': user.address2,
            'contact1': user.contact1,
            'contact2': user.contact2,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }
        users_list.append(user_data)
    
    return Response({
        'status': 'success',
        'count': len(users_list),
        'users': users_list
    }, status=status.HTTP_200_OK)
        
    
#user login view
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Authenticate user
            try:
                user = User.objects.get(email=email)
                
                # Verify password against hashed password
                if user.check_password(password):
                    # Generate JWT tokens with custom claims
                    tokens = get_tokens_for_user(user)
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Login successful',
                        'userID': user.userID,
                        'email': user.email,
                        "is_staff": user.is_staff,
                        'access': tokens['access'],
                        'refresh': tokens['refresh']
                    }, status=200)
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid credentials'
                    }, status=401)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials'
                }, status=401)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method is allowed'
    }, status=405)
    
    
    
# users data using user id 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        user_data = {
            'id': user.id,
            'userID': user.userID,
            'companyName': user.companyName,
            'ownerName': user.ownerName,
            'email': user.email,
            'country': user.country,
            'zipcode': user.zipcode,
            'state': user.state,
            'city': user.city,
            'address1': user.address1,
            'address2': user.address2,
            'contact1': user.contact1,
            'contact2': user.contact2,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return Response({
            'status': 'success',
            'user': user_data
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
