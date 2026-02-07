import uuid
from rest_framework import serializers
from .models import Manifest


class ManifestSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=True)
	manifest_no = serializers.CharField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)
	status = serializers.CharField(read_only=True)
	user = serializers.CharField(source='user.userID', read_only=True)
	receiver_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	destination = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	manual_cn = serializers.CharField(required=False, allow_blank=True, allow_null=True)

	class Meta:
		model = Manifest
		fields = [
			'id', 'manifest_no', 'cnNumbers', 'status', 'created_at', 'user',
			'receiver_name', 'destination', 'manual_cn'
		]

	def create(self, validated_data):
		# Set user from request context
		request = self.context.get('request')
		if request and request.user:
			validated_data['user'] = request.user
		return super().create(validated_data)