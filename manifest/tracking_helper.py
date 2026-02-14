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
            remarks=remarks or generate_tracking_remarks(status, location, updated_by),
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
        
        # Create remarks message based on status
        remarks = generate_tracking_remarks(tracking_status, location, updated_by)
        
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


def generate_tracking_remarks(tracking_status, location, updated_by):
    """
    Generate tracking remarks in the required format with status and date/time.

    Format Examples:
    - Booked: "Booked Packet\nFeb 11, 2026, 08:51 AM • Jhapa • Updated by Ahmed\nStatus updated"
    - In Transit: "In Transit\nFeb 11, 2026, 09:12 AM • Updated by System\nStatus updated"
    - Picked Up: "Packet arrived at Kathmandu\nFeb 11, 2026, 09:12 AM • Kathmandu • Updated by Ahmed Khan\nStatus updated"
    - Arrived to destination: "Arrived at Location\nFeb 11, 2026, 10:30 AM • Location • Updated by Pokhara Branch\nStatus updated"

    Args:
        tracking_status: The tracking status
        location: The location
        updated_by: Who updated the status

    Returns:
        Formatted remarks string
    """
    from django.utils import timezone

    now = timezone.now()
    formatted_datetime = now.strftime('%b %d, %Y, %I:%M %p')
    clean_location = (location or '').strip()

    normalized_status = (tracking_status or '').strip().lower()

    if normalized_status == 'booked':
        status_line = 'Booked Packet'
    elif normalized_status in ('collected'):
        status_line = "Arrived at location"
    elif normalized_status == 'arrived to destination':
        status_line = f"Arrived at {clean_location}" if clean_location else 'Arrived at destination'
    else:
        status_line = tracking_status

    if clean_location:
        details_line = f"{formatted_datetime} • {clean_location} • Updated by {updated_by}"
    else:
        details_line = f"{formatted_datetime} • Updated by {updated_by}"

    return f"{status_line}\n{details_line}\nStatus updated"


def map_manifest_status_to_tracking_status(manifest_status):
    """
    Map manifest status to ShipmentTracking status choices
    
    Mapping:
    In Transit -> In Transit (when manifest created)
    Collected -> Picked Up (when collected at branch)
    Arrived -> Arrived to destination
    Delivered -> Delivered
    On Hold -> On Hold
    Cancelled -> Cancelled
    """
    status_map = {
        'pending': 'Booked',
        'in transit': 'In Transit',
        'collected': 'Picked Up',
        'arrived': 'Arrived to destination',
        'delivered': 'Delivered',
        'on hold': 'On Hold',
        'cancelled': 'Cancelled',
    }

    normalized_status = (manifest_status or '').strip().lower()
    return status_map.get(normalized_status, manifest_status)


def create_initial_tracking_for_manifest(manifest, updated_by):
    """
    Create initial tracking records when manifest is created with CNs
    This marks the CNs as "In Transit" when manifest is created
    
    Args:
        manifest: The Manifest object
        updated_by: Name of person who created the manifest (usually will be shown as "System")
    """
    if not manifest.cnNumbers:
        return
    
    cn_list = [cn.strip() for cn in manifest.cnNumbers.split(',') if cn.strip()]
    
    tracking_records = []
    for cn in cn_list:
        location = manifest.location or ''
        # Create "In Transit" tracking when manifest is created
        remarks = generate_tracking_remarks('In Transit', location, 'System')
        
        tracking = create_tracking_record(
            cn_number=cn,
            status='In Transit',
            location=location,
            updated_by='System',
            remarks=remarks
        )
        
        if tracking:
            tracking_records.append(tracking)
    
    return tracking_records
