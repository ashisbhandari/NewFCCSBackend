from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShipmentSerializer
from .models import Shipment


# Create your views here.

@csrf_exempt
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def View_Product(request):
    shipments = Shipment.objects.all()
    for s in shipments:
        print(s.product_id, s.booked_by, s.date)
        print(s.sender.name, s.receiver.name)
        for piece in s.pieces_detail.all():
            print(piece.piece_number, piece.weight)
    
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK    )
