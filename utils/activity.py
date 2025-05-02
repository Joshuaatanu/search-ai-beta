"""
Activity tracking utilities for login and user sessions.
"""
import requests
from datetime import datetime
from user_agents import parse
import logging

def get_location_from_ip(ip_address):
    """
    Get location information from IP address using ipapi.co
    """
    try:
        # Skip for localhost/private IPs
        if ip_address in ['127.0.0.1', 'localhost', '::1'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            return {
                'city': 'Local',
                'region': 'Local',
                'country': 'Local',
                'timezone': 'Local'
            }
            
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'timezone': data.get('timezone', 'Unknown')
            }
        else:
            logging.error(f"Failed to get location data: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error getting location data: {e}")
        return None

def get_device_info(user_agent_string):
    """
    Parse user agent string to get device information
    """
    try:
        user_agent = parse(user_agent_string)
        return {
            'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
            'os': f"{user_agent.os.family} {user_agent.os.version_string}",
            'device': user_agent.device.family,
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_pc': user_agent.is_pc
        }
    except Exception as e:
        logging.error(f"Error parsing user agent: {e}")
        return None

def track_login_activity(db, user_id, request, success=True):
    """
    Track login activity including location and device information
    """
    try:
        # Get IP address
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Get location data
        location = get_location_from_ip(ip_address)
        
        # Get device information
        device_info = get_device_info(request.headers.get('User-Agent', ''))
        
        # Create activity record
        activity = {
            'user_id': user_id,
            'timestamp': datetime.utcnow(),
            'ip_address': ip_address,
            'location': location,
            'device_info': device_info,
            'success': success,
            'type': 'login'
        }
        
        # Store in database
        db.login_activity.insert_one(activity)
        
        return True
    except Exception as e:
        logging.error(f"Error tracking login activity: {e}")
        return False

def get_login_history(db, user_id, limit=10):
    """
    Get login history for a user
    """
    try:
        history = list(db.login_activity.find(
            {'user_id': user_id},
            {'_id': 0}  # Exclude MongoDB ID
        ).sort('timestamp', -1).limit(limit))
        
        return history
    except Exception as e:
        logging.error(f"Error getting login history: {e}")
        return [] 