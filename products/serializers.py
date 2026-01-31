import uuid
from rest_framework import serializers
from .models import Shipment, Sender, Receiver, ShipmentPiece

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


# Shipment serializers
class ShipmentSerializer(serializers.ModelSerializer):
    sender = SenderSerializer()
    receiver = ReceiverSerializer()
    pieces_detail = ShipmentPieceSerializer(many=True)
    product_id = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'

    def create(self, validated_data):
        sender_data = validated_data.pop('sender')
        receiver_data = validated_data.pop('receiver')
        pieces_data = validated_data.pop('pieces_detail')

        if not validated_data.get('product_id'):
            validated_data['product_id'] = f"TEMP-{uuid.uuid4().hex[:12]}"

        shipment = Shipment.objects.create(**validated_data)

        if shipment.product_id.startswith("TEMP-"):
            base_number = 1000
            shipment.product_id = f"FCCS-{base_number + shipment.id}"
            shipment.save(update_fields=["product_id"])

        Sender.objects.create(shipment=shipment, **sender_data)
        Receiver.objects.create(shipment=shipment, **receiver_data)

        for piece in pieces_data:
            ShipmentPiece.objects.create(shipment=shipment, **piece)

        return shipment
