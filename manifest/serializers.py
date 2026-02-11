import uuid
from rest_framework import serializers
from .models import Manifest


class ManifestSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=True)
	manifest_no = serializers.CharField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)
	updated_at = serializers.DateTimeField(read_only=True)
	status = serializers.CharField(read_only=True)
	user = serializers.CharField(source='user.userID', read_only=True)
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	contact_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	location = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	device_info = serializers.CharField(read_only=True)
	ip_address = serializers.CharField(read_only=True)
	latitude = serializers.FloatField(required=False, allow_null=True)
	longitude = serializers.FloatField(required=False, allow_null=True)

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