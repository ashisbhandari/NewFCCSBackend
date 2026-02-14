from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Manifest
from .tracking_helper import generate_tracking_remarks
from products.models import Shipment, ShipmentTracking


@receiver(post_save, sender=Manifest)
def update_shipment_status_on_manifest_creation(sender, instance, created, **kwargs):
    """
    Automatically update shipment status to 'In Transit' when manifest is created
    """
    if created:  # Only on manifest creation
        # Parse CN numbers (comma-separated)
        cn_list = []
        
        # Get CNs from cnNumbers field
        if instance.cnNumbers:
            cn_list.extend([cn.strip() for cn in instance.cnNumbers.split(',') if cn.strip()])
        
        # Update status for each shipment
        for cn_number in cn_list:
            try:
                shipment = Shipment.objects.get(product_id=cn_number)
                
                # Add "In Transit" tracking entry
                remarks = generate_tracking_remarks('In Transit', instance.location or '', 'System')
                ShipmentTracking.objects.create(
                    shipment=shipment,
                    status='In Transit',
                    location='',
                    origin=shipment.origin if shipment.origin else '',
                    destination=shipment.destination_district if shipment.destination_district else '',
                    remarks=remarks,
                    updated_by='System'
                )
            except Shipment.DoesNotExist:
                # Skip if shipment not found
                pass
