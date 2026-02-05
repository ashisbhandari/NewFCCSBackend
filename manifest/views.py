from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
def update_manifest_status(request, manifest_id):
    try:
        if request.user.is_staff or Manifest.objects.get(manifest_id=manifest_id).user == request.user:
            manifest = Manifest.objects.get(manifest_id=manifest_id)
        else:
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
        manifest.status = 'Collected'
        manifest.save()
        serializer = ManifestSerializer(manifest)
        return Response(
            {
                'message': 'Manifest status updated to Collected',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            'message': 'Only PATCH method is allowed'
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )