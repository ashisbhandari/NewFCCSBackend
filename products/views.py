from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShipmentSerializer, ShipmentTrackingSerializer
from .models import Shipment, ShipmentTracking
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def tracking_status_options(request):
    options = [
        {
            'value': value,
            'label': label
        }
        for value, label in ShipmentTracking.STATUS_CHOICES
    ]

    return Response(
        {
            'message': 'Tracking status options retrieved successfully',
            'data': options
        },
        status=status.HTTP_200_OK
    )

@csrf_exempt
@api_view(['POST'])

def add_Product(request):
    if request.method == 'POST':
        serializer = ShipmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shipment = serializer.save()
            # Re-fetch with related data to get sender/receiver in response
            shipment = Shipment.objects.select_related('sender', 'receiver', 'user').prefetch_related('pieces_detail', 'tracking_history').get(pk=shipment.pk)
            response_serializer = ShipmentSerializer(shipment)
            return Response(
                {
                    'message': 'Product added successfully!',
                    'data': response_serializer.data
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
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny])
@api_view(['GET'])
def View_Product(request):
    # If admin/staff or unauthenticated, show all records; otherwise show user's records
    if not request.user.is_authenticated or request.user.is_staff:
        shipments = Shipment.objects.select_related('sender', 'receiver', 'user').prefetch_related('pieces_detail', 'tracking_history').all()
    else:
        shipments = Shipment.objects.select_related('sender', 'receiver', 'user').prefetch_related('pieces_detail', 'tracking_history').filter(user_id=request.user.id)
    
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data)

# view a single product detail using product id
@api_view(['GET'])
@permission_classes([AllowAny])
def product_by_id(request, product_id):
    try:
        # Prefer product_id lookup first, then fallback to pk for numeric input
        try:
            shipment = Shipment.objects.select_related('sender', 'receiver', 'user').prefetch_related('pieces_detail', 'tracking_history').get(product_id=product_id)
        except Shipment.DoesNotExist:
            if product_id.isdigit():
                shipment = Shipment.objects.select_related('sender', 'receiver', 'user').prefetch_related('pieces_detail', 'tracking_history').get(pk=int(product_id))
            else:
                raise
    except Shipment.DoesNotExist:
        return Response(
            {
                'message': 'Product not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ShipmentSerializer(shipment)
    return Response(serializer.data)


# add tracking update to a shipment
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_tracking_update(request, product_id):
    try:
        shipment = Shipment.objects.get(product_id=product_id)
    except Shipment.DoesNotExist:
        return Response(
            {
                'message': 'Shipment not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'POST':
        tracking_data = request.data.copy()
        tracking_data['shipment'] = shipment.id
        
        # Auto-fill origin and destination from shipment if not provided
        if not tracking_data.get('origin'):
            tracking_data['origin'] = shipment.origin if shipment.origin else ''
        if not tracking_data.get('destination'):
            tracking_data['destination'] = shipment.destination_district if shipment.destination_district else ''
        
        # Set updated_by from authenticated user
        if not tracking_data.get('updated_by'):
            tracking_data['updated_by'] = request.user.companyName if hasattr(request.user, 'companyName') else request.user.email
        
        serializer = ShipmentTrackingSerializer(data=tracking_data)
        if serializer.is_valid():
            serializer.save(shipment=shipment)
            return Response(
                {
                    'message': 'Tracking update added successfully!',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Failed to add tracking update',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# view tracking history by shipment id or product id
@api_view(['GET'])
@permission_classes([AllowAny])
def view_tracking_history(request, identifier):
    shipment = None

    if identifier.isdigit():
        shipment = Shipment.objects.filter(pk=int(identifier)).first()

    if shipment is None:
        shipment = Shipment.objects.filter(product_id=identifier).first()

    if shipment is None:
        return Response(
            {
                'message': 'Shipment not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    tracking = ShipmentTracking.objects.filter(shipment=shipment).order_by('-timestamp')
    tracking_serializer = ShipmentTrackingSerializer(tracking, many=True)

    return Response(
        {
            'product_id': shipment.product_id,
            'origin': shipment.origin,
            'destination': shipment.destination_district,
            'tracking_history': tracking_serializer.data
        },
        status=status.HTTP_200_OK
    )
    
    
# update tracking history by tracking id
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tracking(request, identifier):
    tracking = None

    if identifier.isdigit():
        tracking = ShipmentTracking.objects.select_related('shipment__receiver', 'shipment__sender').filter(id=int(identifier)).first()

    if tracking is None:
        shipment = Shipment.objects.select_related('receiver', 'sender').filter(product_id=identifier).first()
        if shipment:
            tracking = ShipmentTracking.objects.select_related('shipment__receiver', 'shipment__sender').filter(shipment=shipment).order_by('-timestamp').first()

    if tracking is None:
        return Response(
            {
                'message': 'Tracking record not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'PUT':
        tracking_data = request.data.copy()

        # Optional contact details to update on receiver (fallback sender)
        contact_name = tracking_data.get('name')
        contact_number = tracking_data.get('number') or tracking_data.get('contact_number')

        if 'name' in tracking_data:
            tracking_data.pop('name')
        if 'number' in tracking_data:
            tracking_data.pop('number')
        if 'contact_number' in tracking_data:
            tracking_data.pop('contact_number')
        
        # Set updated_by from authenticated user if not provided
        if not tracking_data.get('updated_by'):
            tracking_data['updated_by'] = request.user.companyName if hasattr(request.user, 'companyName') else request.user.email
        
        serializer = ShipmentTrackingSerializer(tracking, data=tracking_data, partial=True)
        if serializer.is_valid():
            serializer.save()

            shipment = tracking.shipment
            receiver = getattr(shipment, 'receiver', None)
            sender = getattr(shipment, 'sender', None)
            contact_target = receiver or sender

            if contact_target and (contact_name or contact_number):
                update_fields = []
                if contact_name:
                    contact_target.name = contact_name
                    update_fields.append('name')
                if contact_number:
                    contact_target.phone = contact_number
                    update_fields.append('phone')
                if update_fields:
                    contact_target.save(update_fields=update_fields)

            response_name = ''
            response_number = ''
            if receiver:
                response_name = receiver.name or ''
                response_number = receiver.phone or ''
            elif sender:
                response_name = sender.name or ''
                response_number = sender.phone or ''

            return Response(
                {
                    'message': 'Tracking update modified successfully!',
                    'name': response_name,
                    'number': response_number,
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Failed to modify tracking update',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )