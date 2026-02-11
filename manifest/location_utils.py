"""
Utility functions to extract location and device information from request
"""
from user_agents import parse
from geopy.geocoders import Nominatim
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    """
    Extract device information from User-Agent header
    Returns a string with device type, OS, and browser info
    """
    user_agent_string = request.META.get('HTTP_USER_AGENT', 'Unknown')
    user_agent = parse(user_agent_string)
    
    device_type = user_agent.device.family  # e.g., 'iPhone', 'Samsung', 'Windows'
    os = user_agent.os.family  # e.g., 'iOS', 'Android', 'Windows'
    browser = user_agent.browser.family  # e.g., 'Chrome', 'Safari', 'Firefox'
    
    device_info = f"{device_type} | {os} | {browser}"
    return device_info


def get_address_from_coordinates(latitude, longitude):
    """
    Convert GPS coordinates to readable address using reverse geocoding
    """
    try:
        geolocator = Nominatim(user_agent="manifest_tracker")
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en', timeout=5)
        return location.address
    except Exception as e:
        logger.warning(f"Failed to reverse geocode coordinates: {e}")
        return f"Lat: {latitude}, Long: {longitude}"


def get_location_from_request(request):
    """
    Get location from request data:
    1. If GPS coordinates are provided, convert them to address
    2. Otherwise use provided location string
    3. Fallback to a generic location message
    """
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    location = request.data.get('location')
    
    # If GPS coordinates are provided, convert to address
    if latitude and longitude:
        try:
            address = get_address_from_coordinates(float(latitude), float(longitude))
            return address, float(latitude), float(longitude)
        except Exception as e:
            logger.warning(f"Error processing GPS coordinates: {e}")
    
    # Use provided location string
    if location:
        return location, latitude, longitude
    
    # Fallback: use IP-based location info (can be enhanced with MaxMind GeoIP2)
    return "Location not provided", latitude, longitude


def extract_location_and_device(request):
    """
    Main function to extract all location and device information from request
    Returns a dict with location, device_info, ip_address, latitude, and longitude
    """
    ip_address = get_client_ip(request)
    device_info = get_device_info(request)
    location, latitude, longitude = get_location_from_request(request)
    
    return {
        'location': location,
        'device_info': device_info,
        'ip_address': ip_address,
        'latitude': latitude,
        'longitude': longitude,
    }
