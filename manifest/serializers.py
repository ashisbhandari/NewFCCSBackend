import uuid
from rest_framework import serializers
from .models import Manifest


class ManifestSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=True)
	manifest_no = serializers.CharField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)
	updated_at = serializers.DateTimeField(read_only=True)
	status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	user = serializers.CharField(source='user.userID', read_only=True)
	name = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # User's name
	contact_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # User's contact number
	location = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # User provides location
	device_info = serializers.CharField(read_only=True)  # Device info (auto-captured on status update)
	ip_address = serializers.CharField(read_only=True)  # IP address (auto-captured on status update)
	latitude = serializers.FloatField(required=False, allow_null=True)  # GPS latitude (user provides or auto on status update)
	longitude = serializers.FloatField(required=False, allow_null=True)  # GPS longitude (user provides or auto on status update)

	class Meta:
		model = Manifest
		fields = [
			'id', 'manifest_no', 'cnNumbers', 'status', 'created_at', 'updated_at', 'user',
			'name', 'contact_number', 'location', 'device_info', 'ip_address', 'latitude', 'longitude'
		]

	def create(self, validated_data):
		# Set user from request context
		request = self.context.get('request')
		if request and request.user:
			validated_data['user'] = request.user
		return super().create(validated_data)