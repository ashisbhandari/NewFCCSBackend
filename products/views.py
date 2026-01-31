from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShipmentSerializer
from .models import Shipment
from rest_framework.decorators import api_view


# Create your views here.

@csrf_exempt
@api_view(['POST'])

def add_Product(request):
    if request.method == 'POST':
        serializer = ShipmentSerializer(data=request.data)
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


@api_view(['GET'])
def View_Product(request):
    shipments = Shipment.objects.all()
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data)
