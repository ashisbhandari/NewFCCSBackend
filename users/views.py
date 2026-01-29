from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

# default user function view
def user_dashboard(request):
    data = {
        "message": "hello",
        "status": "success",
        "user": "dashboard_user"
    }
    return JsonResponse(data)

# add user by admin
@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            
            # Create new user
            contact1 = data.get('contact1')
            user = User.objects.create(
                companyName=data.get('companyName'),
                ownerName=data.get('ownerName'),
                email=data.get('email'),
                country=data.get('country'),
                Zipcode=data.get('Zipcode'),
                state=data.get('state'),
                city=data.get('city'),
                address1=data.get('address1'),
                address2=data.get('address2', ''),
                contact1=contact1,
                contact2=data.get('contact2', ''),
                password=contact1,  # Automatically set password to contact1
                is_staff=False  # Always set to False when adding users
            )
            
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
                user = User.objects.get(email=email, password=password)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Login successful',
                    'userID': user.userID,
                    'email': user.email,
                    "is_staff": user.is_staff,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=200)
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