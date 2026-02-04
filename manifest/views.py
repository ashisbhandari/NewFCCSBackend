from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

def home(request):
    data = {
        "message": "hello manifest page is active",
        "status": "success",
        "user": "dashboard_invoice"
    }
    return JsonResponse(data)

def add_manifest(request):
    data = {
        "message": "add manifest page is active",
        "status": "success",
        "user": "add_manifest_user"
    }
    return JsonResponse(data)