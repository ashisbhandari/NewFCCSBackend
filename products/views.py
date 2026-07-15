from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShipmentSerializer, ShipmentTrackingSerializer
from .models import Shipment, ShipmentTracking
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from manifest.tracking_helper import generate_tracking_remarks


# Create your views here.

def home(request):
    data = {
        "message": "Welcome to the FCCS Product Page, Server is running smoothly!"
    }
    return render(request, 'home.html', data)

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

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_product(request, product_id):
    try:
        shipment = Shipment.objects.get(product_id=product_id)
    except Shipment.DoesNotExist:
        return Response(
            {
                'message': 'Product not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'PUT':
        serializer = ShipmentSerializer(shipment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_shipment = serializer.save()
            # Re-fetch with related data to get sender/receiver in response
            updated_shipment = Shipment.objects.select_related('sender', 'receiver', 'user').prefetch_related('pieces_detail', 'tracking_history').get(pk=updated_shipment.pk)
            response_serializer = ShipmentSerializer(updated_shipment)
            return Response(
                {
                    'message': 'Product updated successfully!',
                    'data': response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Failed to update product',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {
            'message': 'Only PUT method is allowed'
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
    

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
        latest_tracking = ShipmentTracking.objects.filter(shipment=shipment).order_by('-timestamp').first()
        if latest_tracking and latest_tracking.status == 'Cancelled':
            return Response(
                {
                    'message': 'Shipment is already cancelled. No further tracking updates are allowed.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tracking_data = request.data.copy()

        # Set updated_by from authenticated user
        updated_by = tracking_data.get('updated_by')
        if not updated_by:
            updated_by = request.user.companyName if hasattr(request.user, 'companyName') and request.user.companyName else request.user.email
            tracking_data['updated_by'] = updated_by

        # Auto-fill location from shipment origin if not provided
        if not tracking_data.get('location'):
            tracking_data['location'] = shipment.origin if shipment.origin else ''

        # Support either remarks or message in request payload
        if not tracking_data.get('remarks') and tracking_data.get('message'):
            tracking_data['remarks'] = tracking_data.get('message')

        # Auto-generate remarks if none is provided
        if not tracking_data.get('remarks'):
            tracking_data['remarks'] = generate_tracking_remarks(
                tracking_data.get('status', ''),
                tracking_data.get('location', ''),
                updated_by or 'System'
            )

        serializer = ShipmentTrackingSerializer(data=tracking_data)
        if serializer.is_valid():
            tracking_record = serializer.save(
                shipment=shipment,
                origin=shipment.origin if shipment.origin else '',
                destination=shipment.destination_district if shipment.destination_district else ''
            )

            response_serializer = ShipmentTrackingSerializer(tracking_record)
            return Response(
                {
                    'message': 'Tracking update added successfully!',
                    'data': response_serializer.data
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
    
    
# CANCEL A SHIPMENT (soft delete by setting status to 'Cancelled') AND MAKE THE UPDATE DISABLE FOR FURTHER TRACKING UPDATES
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_tracking(request, identifier):
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

    latest_tracking = ShipmentTracking.objects.filter(shipment=shipment).order_by('-timestamp').first()
    if latest_tracking and latest_tracking.status == 'Cancelled':
        return Response(
            {
                'message': 'Shipment is already cancelled.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    new_status = request.data.get('status', 'Cancelled')
    if new_status != 'Cancelled':
        return Response(
            {
                'message': 'Only status update to "Cancelled" is allowed'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    updated_by = request.data.get('updated_by')
    if not updated_by:
        updated_by = request.user.companyName if hasattr(request.user, 'companyName') and request.user.companyName else request.user.email

    location = request.data.get('location') or (shipment.origin if shipment.origin else '')
    remarks = request.data.get('remarks') or request.data.get('message')
    if not remarks:
        remarks = generate_tracking_remarks('Cancelled', location, updated_by or 'System')

    tracking = ShipmentTracking.objects.create(
        shipment=shipment,
        status='Cancelled',
        location=location,
        origin=shipment.origin if shipment.origin else '',
        destination=shipment.destination_district if shipment.destination_district else '',
        remarks=remarks,
        updated_by=updated_by
    )

    return Response(
        {
            'message': 'Shipment cancelled successfully!',
            'data': ShipmentTrackingSerializer(tracking).data
        },
        status=status.HTTP_200_OK
    )