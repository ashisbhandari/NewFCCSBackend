from django.http import JsonResponse

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
def add_user(request):
    data = {
        "message": "Add User Functionality to be implemented",
        "status": "success"
    }
    return JsonResponse(data)