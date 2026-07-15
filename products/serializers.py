import uuid
from rest_framework import serializers
from manifest.tracking_helper import generate_tracking_remarks
from .models import Shipment, Sender, Receiver, ShipmentPiece, ShipmentTracking

# sender sealizers
class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sender
        fields = ['name', 'phone', 'email', 'address1', 'address2']

# receiver sealizers
class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receiver
        fields = ['name', 'phone', 'email', 'address1', 'address2']

# ShipmentPiece serializers
class ShipmentPieceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentPiece
        fields = ['piece_number', 'weight']

# ShipmentTracking serializers
class ShipmentTrackingSerializer(serializers.ModelSerializer):
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ShipmentTracking
        fields = ['id', 'status', 'location', 'remarks', 'timestamp', 'updated_by']
        read_only_fields = ['id', 'timestamp']


# Shipment serializers
class ShipmentSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(allow_null=True)
    receiver = ReceiverSerializer(allow_null=True)
    pieces_detail = ShipmentPieceSerializer(many=True)
    tracking_history = ShipmentTrackingSerializer(many=True, read_only=True)
    product_id = serializers.CharField(required=False, allow_blank=False)
    user = serializers.CharField(source='user.companyName', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    origin = serializers.CharField(required=False, read_only=True)
    destination = serializers.CharField(source='destination_district', read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'

    def validate_product_id(self, value):
        queryset = Shipment.objects.filter(product_id=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError('Product ID already exists.')
        return value

    def create(self, validated_data):
        sender_data = validated_data.pop('sender')
        receiver_data = validated_data.pop('receiver')
        pieces_data = validated_data.pop('pieces_detail', [])

        # Automatically set the user from the request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            # Automatically set user_id_custom from user's userID
            if hasattr(request.user, 'userID') and request.user.userID:
                validated_data['user_id_custom'] = request.user.userID
            # Automatically set origin from user's city
            if hasattr(request.user, 'city') and request.user.city:
                validated_data['origin'] = request.user.city

        if not validated_data.get('product_id'):
            validated_data['product_id'] = f"TEMP-{uuid.uuid4().hex[:12]}"

        shipment = Shipment.objects.create(**validated_data)

        if shipment.product_id.startswith("TEMP-"):
            base_number = 1000
            shipment.product_id = f"FCCS {base_number + shipment.id}"
            shipment.save(update_fields=["product_id"])

        Sender.objects.create(shipment=shipment, **sender_data)
        Receiver.objects.create(shipment=shipment, **receiver_data)

        for piece in pieces_data:
            ShipmentPiece.objects.create(shipment=shipment, **piece)

        # Create initial tracking entry
        updated_by = shipment.booked_by if shipment.booked_by else 'System'
        remarks = generate_tracking_remarks('Booked', shipment.origin if shipment.origin else '', updated_by)
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='Booked',
            location=shipment.origin if shipment.origin else '',
            origin=shipment.origin if shipment.origin else '',
            destination=shipment.destination_district if shipment.destination_district else '',
            remarks=remarks,
            updated_by=updated_by
        )

        
        return shipment

    def update(self, instance, validated_data):
        sender_data = validated_data.pop('sender', None)
        receiver_data = validated_data.pop('receiver', None)
        pieces_data = validated_data.pop('pieces_detail', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if sender_data is not None:
            try:
                sender = instance.sender
            except Sender.DoesNotExist:
                Sender.objects.create(shipment=instance, **sender_data)
            else:
                for attr, value in sender_data.items():
                    setattr(sender, attr, value)
                sender.save()

        if receiver_data is not None:
            try:
                receiver = instance.receiver
            except Receiver.DoesNotExist:
                Receiver.objects.create(shipment=instance, **receiver_data)
            else:
                for attr, value in receiver_data.items():
                    setattr(receiver, attr, value)
                receiver.save()

        if pieces_data is not None:
            instance.pieces_detail.all().delete()
            for piece in pieces_data:
                ShipmentPiece.objects.create(shipment=instance, **piece)

        return instance
