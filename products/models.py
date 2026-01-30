from django.db import models


class Shipment(models.Model):
    PACKET_TYPES = [
        ('Document', 'Document'),
        ('Parcel', 'Parcel'),
        ('Box', 'Box'),
        ('Bora', 'Bora'),
    ]

    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Mobile Payment', 'Mobile Payment'),
        ('Bank Transfer', 'Bank Transfer'),
    ]

    SERVICE_TYPES = [
        ('Home delivery', 'Home delivery'),
        ('Office Collection', 'Office Collection'),
    ]

    product_id = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)

    packet_type = models.CharField(max_length=20, choices=PACKET_TYPES)
    destination_district = models.CharField(max_length=100)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)

    pieces = models.PositiveIntegerField()
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField(blank=True, null=True)
    booked_by = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_id


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
