from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShipmentSerializer
from .models import Shipment
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# Create your views here.

@csrf_exempt
@api_view(['POST'])

def add_Product(request):
    if request.method == 'POST':
        serializer = ShipmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Product added successfully!',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Failed to add product',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {
            'message': 'Only POST method is allowed'
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )

# view all product details (admin) or user-specific products
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def View_Product(request):
    # If admin/staff, show all records; otherwise show user's records
    if request.user.is_staff:
        shipments = Shipment.objects.all()
    else:
        shipments = Shipment.objects.filter(user_id=request.user.id)
    
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data)

# view a single product detail using product id
@api_view(['GET'])
def product_by_id(request, product_id):
    try:
        # First try to fetch by numeric ID
        if product_id.isdigit():
            shipment = Shipment.objects.get(pk=int(product_id))
        else:
            # If not numeric, try to fetch by product_id field (handles "fccs 9" or "fccs9")
            shipment = Shipment.objects.get(product_id=product_id)
    except Shipment.DoesNotExist:
        return Response(
            {
                'message': 'Product not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ShipmentSerializer(shipment)
    return Response(serializer.data)