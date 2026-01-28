from django.shortcuts import render


def home(request):
    data = {
        "message": "Welcome to the FCCS Home Page, Server is running smoothly!"
    }
    return render(request, "home.html", data)
