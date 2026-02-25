from django.db import models
from users.models import User


class Shipment(models.Model):
    PACKET_TYPES = [
        ('Document', 'Document'),
        ('Parcel', 'Parcel'),
        ('Box', 'Box'),
        ('Bora', 'Bora'),
    ]

    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online Payment', 'Online Payment'),
    ]

    SERVICE_TYPES = [
        ('Home delivery', 'Home delivery'),
        ('Office Collection', 'Office Collection'),
    ]

    product_id = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)

    packet_type = models.CharField(max_length=20, choices=PACKET_TYPES)
    destination_district = models.CharField(max_length=100)
    origin = models.CharField(max_length=100, null=True, blank=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)

    pieces = models.PositiveIntegerField()
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField(blank=True, null=True)
    booked_by = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='shipments', null=True, blank=True)
    user_id_custom = models.CharField(max_length=20, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_id
    class Meta:
        db_table = 'shipments'


class Sender(models.Model):
    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name="sender"
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Receiver(models.Model):
    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name="receiver"
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class ShipmentPiece(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="pieces_detail"
    )

    piece_number = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.shipment.product_id} - Piece {self.piece_number}"


class ShipmentTracking(models.Model):
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Picked Up', 'Picked Up'),
        ('In Transit', 'In Transit'),
        ('Arrived to destination', 'Arrived to destination'),
        ('Delivered', 'Delivered'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),
    ]

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="tracking_history"
    )

    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    location = models.CharField(max_length=255, blank=True, null=True)
    origin = models.CharField(max_length=255, blank=True, null=True)
    destination = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'shipment_tracking'

    def __str__(self):
        return f"{self.shipment.product_id} - {self.status} at {self.timestamp}"
