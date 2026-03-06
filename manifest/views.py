from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from manifest.models import Manifest
from .serializers import ManifestSerializer
from .location_utils import extract_location_and_device
from .tracking_helper import create_manifest_tracking_records, create_initial_tracking_for_manifest

# Create your views here.

def home(request):
    data = {
        "message": "Serveer is active",
        "status": "success",
        "user": "dashboard_invoice"
    }
    return JsonResponse(data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_manifest(request):
    
    if request.method == 'POST':
        # Only accept cnNumbers from user
        data = {'cnNumbers': request.data.get('cnNumbers')}
        serializer = ManifestSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            try:
                manifest = serializer.save()
                
                # Refresh manifest from database to get the newly generated manifest_no
                manifest.refresh_from_db()
                
                return Response(
                    {
                        'message': 'Manifest created successfully!',
                        'data': ManifestSerializer(manifest).data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {
                        'message': 'Error creating manifest',
                        'error': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {
                'message': 'Failed to add manifest',
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
    
# view manifest
# if user is admin then show all manifest else show user specific manifest
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_manifests(request):
    if request.method == 'GET':
        if request.user.is_staff:
            manifests = Manifest.objects.all()
        else:
            manifests = Manifest.objects.filter(user=request.user)
        serializer = ManifestSerializer(manifests, many=True)
        return Response(
            {
                'message': 'Manifests retrieved successfully!',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            'message': 'Only GET method is allowed'
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
    
# update the status of manifest
# User provides: status (required), name, contact_number, location (optional)
# System auto-captures: device_info, ip_address, and optionally location from GPS
# Tracking records are automatically created for all CNs
@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_manifest_status(request, manifest_no):
    """
    Update manifest status and create tracking records for all CNs
    
    Required: status
    Optional: name, contact_number, location
    Auto-captured: device_info, ip_address (latitude/longitude if not provided)
    """
    try:
        manifest = Manifest.objects.get(manifest_no=manifest_no)
    except Manifest.DoesNotExist:
        return Response(
            {
                'message': 'Manifest not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'PATCH':
        new_status = request.data.get('status')
        if new_status:
            manifest.status = new_status
            
            # Update user-provided information (name and contact_number)
            if 'name' in request.data:
                manifest.name = request.data.get('name')
            if 'contact_number' in request.data:
                manifest.contact_number = request.data.get('contact_number')
            
            # Update location from user input if provided
            if 'location' in request.data:
                manifest.location = request.data.get('location')
            
            # Auto-capture device and IP information from request
            location_device_info = extract_location_and_device(request)
            manifest.device_info = location_device_info['device_info']
            manifest.ip_address = location_device_info['ip_address']
            
            # Update GPS coordinates if provided by user
            if 'latitude' in request.data:
                manifest.latitude = request.data.get('latitude')
            if 'longitude' in request.data:
                manifest.longitude = request.data.get('longitude')
            
            # If location not provided but GPS coordinates are provided, convert to address
            if 'latitude' in request.data and 'longitude' in request.data and 'location' not in request.data:
                try:
                    from .location_utils import get_address_from_coordinates
                    manifest.location = get_address_from_coordinates(
                        float(request.data.get('latitude')),
                        float(request.data.get('longitude'))
                    )
                except:
                    manifest.location = f"Lat: {request.data.get('latitude')}, Long: {request.data.get('longitude')}"
            
            # Save manifest - updated_at will automatically update via auto_now
            manifest.save()
            
            # Create tracking records for all CNs when status changes
            updated_by = manifest.name or request.data.get('name') or 'System'
            create_manifest_tracking_records(
                manifest=manifest,
                status=new_status,
                location=manifest.location,
                updated_by=updated_by
            )
            
            serializer = ManifestSerializer(manifest)
            return Response(
                {
                    'message': f'Manifest status updated to {new_status} and tracking records created',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Status field is required'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {
            'message': 'Only PATCH method is allowed'
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
    
    
# update manifest according to manifest no
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_manifest(request, manifest_no):
    try:
        manifest = Manifest.objects.get(manifest_no=manifest_no)
        if not request.user.is_staff and manifest.user != request.user:
            return Response(
                {
                    'message': 'You do not have permission to update this manifest'
                },
                status=status.HTTP_403_FORBIDDEN
            )
    except Manifest.DoesNotExist:
        return Response(
            {
                'message': 'Manifest not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'PUT':
        # Get user data and location data
        data = request.data.copy()
        
        # If name and contact_number are provided, save them
        if 'name' in data:
            manifest.name = data.get('name')
        if 'contact_number' in data:
            manifest.contact_number = data.get('contact_number')
        
        # Get location from request or use a default placeholder
        if 'location' in data:
            manifest.location = data.get('location')
        else:
            # System auto-fetches location (can be enhanced with geolocation API)
            location = data.get('location', '')
            manifest.location = location
        
        serializer = ManifestSerializer(manifest, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Manifest updated successfully with user information!',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Failed to update manifest',
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
    
# view which only show the cn numbers and pass user record not much more 
@api_view(['GET'])
@permission_classes([AllowAny])
def view_manifest_cn_numbers(request, manifest_no):
    try:
        manifest = Manifest.objects.get(manifest_no=manifest_no)
        
    except Manifest.DoesNotExist:
        return Response(
            {
                'message': 'Manifest not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        cn_numbers = []
        manifest_status = manifest.status
        manifest_user = None
        if manifest.user:
            manifest_user = {
                'userID': manifest.user.userID,
                'ownerName': manifest.user.ownerName,
                'email': manifest.user.email,
            }
        if manifest.cnNumbers:
            cn_numbers.extend([cn.strip() for cn in manifest.cnNumbers.split(',') if cn.strip()])
        
        return Response(
            {
                'user': manifest_user,
                'data': cn_numbers,
                'status': manifest_status
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            'message': 'Only GET method is allowed'
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )