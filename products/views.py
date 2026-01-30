from django.shortcuts import render

# Create your views here.


def add_Product(request):
    if request.method == 'POST':
        pass
    return render(request, 'Product added successfully!')