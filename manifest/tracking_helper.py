"""
Helper functions to create shipment tracking records when manifest status changes
"""
from products.models import Shipment, ShipmentTracking
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def create_tracking_record(cn_number, status, location, updated_by, remarks=None):
    """
    Create a tracking record for a shipment/CN
    
    Args:
        cn_number: The CN/product_id
        status: The status to record
        location: The location where status changed
        updated_by: Name of person who updated the status
        remarks: Additional remarks/notes
    """
    try:
        # Find the shipment by product_id (CN number)
        shipment = Shipment.objects.get(product_id=cn_number)
        
        # Create tracking record
        tracking = ShipmentTracking.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            remarks=remarks or f"Packet {status.lower()} at {location}",
            updated_by=updated_by,
            timestamp=timezone.now()
        )
        
        logger.info(f"Tracking record created for CN: {cn_number}, Status: {status}")
        return tracking
    except Shipment.DoesNotExist:
        logger.warning(f"Shipment not found for CN: {cn_number}")
        return None
    except Exception as e:
        logger.error(f"Error creating tracking record for CN {cn_number}: {str(e)}")
        return None


def create_manifest_tracking_records(manifest, status, location, updated_by):
    """
    Create tracking records for all CNs in a manifest when status changes
    
    Args:
        manifest: The Manifest object
        status: The new status
        location: The location of the status update
        updated_by: Name of person who updated
    """
    if not manifest.cnNumbers:
        return
    
    # Split the CN numbers and create tracking for each
    cn_list = [cn.strip() for cn in manifest.cnNumbers.split(',') if cn.strip()]
    
    tracking_records = []
    for cn in cn_list:
        # Map manifest status to shipment tracking status
        tracking_status = map_manifest_status_to_tracking_status(status)
        
        # Create remarks message
        remarks = f"Packet {tracking_status.lower()} at {location} and updated by {updated_by}"
        
        # Create tracking record
        tracking = create_tracking_record(
            cn_number=cn,
            status=tracking_status,
            location=location,
            updated_by=updated_by,
            remarks=remarks
        )
        
        if tracking:
            tracking_records.append(tracking)
    
    return tracking_records


def map_manifest_status_to_tracking_status(manifest_status):
    """
    Map manifest status to ShipmentTracking status choices
    
    Mapping:
    Pending -> Booked
    Collected -> Picked Up
    In Transit -> In Transit
    Arrived -> Arrived to destination
    Delivered -> Delivered
    On Hold -> On Hold
    Cancelled -> Cancelled
    """
    status_map = {
        'Pending': 'Booked',
        'Collected': 'Picked Up',
        'In Transit': 'In Transit',
        'Arrived': 'Arrived to destination',
        'Delivered': 'Delivered',
        'On Hold': 'On Hold',
        'Cancelled': 'Cancelled',
    }
    
    return status_map.get(manifest_status, manifest_status)


def create_initial_tracking_for_manifest(manifest, updated_by):
    """
    Create initial tracking records when manifest is created with CNs
    This marks the CNs as "Booked"
    
    Args:
        manifest: The Manifest object
        updated_by: Name of person who created the manifest
    """
    if not manifest.cnNumbers:
        return
    
    cn_list = [cn.strip() for cn in manifest.cnNumbers.split(',') if cn.strip()]
    
    tracking_records = []
    for cn in cn_list:
        remarks = f"Packet booked in manifest {manifest.manifest_no} by {updated_by}"
        
        tracking = create_tracking_record(
            cn_number=cn,
            status='Booked',
            location=manifest.location or 'Not specified',
            updated_by=updated_by,
            remarks=remarks
        )
        
        if tracking:
            tracking_records.append(tracking)
    
    return tracking_records
