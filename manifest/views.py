from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from manifest.models import Manifest
from .serializers import ManifestSerializer

# Create your views here.

def home(request):
    data = {
        "message": "hello manifest page is active",
        "status": "success",
        "user": "dashboard_invoice"
    }
    return JsonResponse(data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_manifest(request):
    if request.method == 'POST':
        serializer = ManifestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Manifest added successfully!',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
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
    
# update the status of manifest to collected
# only specific user can update the status
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_manifest_status(request, manifest_no):
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
    
    if request.method == 'PATCH':
        new_status = request.data.get('status')
        if new_status:
            manifest.status = new_status
            manifest.save()
            serializer = ManifestSerializer(manifest)
            return Response(
                {
                    'message': f'Manifest status updated to {new_status}',
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
        serializer = ManifestSerializer(manifest, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Manifest updated successfully!',
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
        if manifest.cnNumbers:
            cn_numbers.extend([cn.strip() for cn in manifest.cnNumbers.split(',') if cn.strip()])
        if manifest.manual_cn:
            cn_numbers.extend([cn.strip() for cn in manifest.manual_cn.split(',') if cn.strip()])
        
        return Response(
            {
                'message': 'CN numbers retrieved successfully!',
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