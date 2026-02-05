import uuid
from rest_framework import serializers
from .models import Manifest


class ManifestSerializer(serializers.ModelSerializer):
	manifest_id = serializers.CharField(read_only=True)
	manifest_no = serializers.CharField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)
	status = serializers.CharField(read_only=True)
	user = serializers.CharField(source='user.userID', read_only=True)

	class Meta:
		model = Manifest
		fields = ['manifest_id', 'manifest_no', 'cnNumbers', 'status', 'created_at', 'user']

	def create(self, validated_data):
		if not validated_data.get('manifest_id'):
			validated_data['manifest_id'] = str(uuid.uuid4().hex[:12])
		# Set user from request context
		request = self.context.get('request')
		if request and request.user:
			validated_data['user'] = request.user
		return super().create(validated_data)