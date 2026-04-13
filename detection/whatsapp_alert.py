"""
WhatsApp Alert System for No Mask Detection
Automatically sends WhatsApp alerts when no mask is detected
"""

import time
import os
from datetime import datetime
from twilio.rest import Client
from django.conf import settings

# Global variable to prevent spam WhatsApp messages
last_whatsapp_time = 0
WHATSAPP_COOLDOWN_PERIOD = 120  # 120 seconds gap between WhatsApp messages (production standard)

def send_whatsapp_alert():
    """
    Send WhatsApp alert for no mask detection
    Includes spam prevention mechanism
    """
    global last_whatsapp_time
    
    try:
        # Get Twilio WhatsApp credentials from environment variables or settings
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))
        whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', os.getenv('TWILIO_WHATSAPP_NUMBER'))
        to_whatsapp_number = getattr(settings, 'ALERT_WHATSAPP_NUMBER', os.getenv('ALERT_WHATSAPP_NUMBER'))
        
        # Check if all required credentials are available
        if not all([account_sid, auth_token, whatsapp_number, to_whatsapp_number]):
            print("WhatsApp Alert Error: Missing Twilio WhatsApp credentials")
            return False
        
        current_time = time.time()
        
        # Spam prevention: Check if enough time has passed since last WhatsApp message
        if current_time - last_whatsapp_time < WHATSAPP_COOLDOWN_PERIOD:
            print(f"WhatsApp Alert: Cooldown active ({WHATSAPP_COOLDOWN_PERIOD}s)")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create timestamp for message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send WhatsApp message with timestamp and location info
        message = client.messages.create(
            from_=f'whatsapp:{whatsapp_number}',
            body=f"! ALERT: No Mask Detected at {timestamp} - Hospital Security System\n\nPlease check the security camera immediately!",
            to=f'whatsapp:{to_whatsapp_number}'
        )
        
        # Update last WhatsApp time
        last_whatsapp_time = current_time
        
        print(f"WhatsApp Alert Sent Successfully! Message SID: {message.sid}")
        print(f"WhatsApp Alert sent at: {timestamp}")
        return True
        
    except Exception as e:
        print(f"WhatsApp Alert Error: {str(e)}")
        return False

def send_whatsapp_with_media(image_path, confidence=None):
    """
    Send WhatsApp alert with screenshot image attachment
    """
    global last_whatsapp_time
    
    try:
        # Get Twilio WhatsApp credentials
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))
        whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', os.getenv('TWILIO_WHATSAPP_NUMBER'))
        to_whatsapp_number = getattr(settings, 'ALERT_WHATSAPP_NUMBER', os.getenv('ALERT_WHATSAPP_NUMBER'))
        
        if not all([account_sid, auth_token, whatsapp_number, to_whatsapp_number]):
            print("WhatsApp Alert Error: Missing Twilio WhatsApp credentials")
            return False
        
        current_time = time.time()
        
        # Spam prevention
        if current_time - last_whatsapp_time < WHATSAPP_COOLDOWN_PERIOD:
            print(f"WhatsApp Alert: Cooldown active ({WHATSAPP_COOLDOWN_PERIOD}s)")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create timestamp for message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare message text
        message_text = f"! ALERT: No Mask Detected at {timestamp}"
        if confidence:
            message_text += f"\nConfidence: {confidence:.1f}%"
        message_text += f"\n\nPlease check the security camera immediately!"
        
        # Check if image file exists
        if not os.path.exists(image_path):
            print(f"WhatsApp Alert: Image file not found: {image_path}")
            return False
        
        # Send WhatsApp message with media
        # Use proper Django media URL format
        media_filename = os.path.basename(image_path)
        media_url = f'http://127.0.0.1:8000/media/no_mask_screenshots/{media_filename}'
        
        print(f"Sending WhatsApp with media URL: {media_url}")
        
        message = client.messages.create(
            from_=f'whatsapp:{whatsapp_number}',
            body=message_text,
            media_url=[media_url],
            to=f'whatsapp:{to_whatsapp_number}'
        )
        
        # Update last WhatsApp time
        last_whatsapp_time = current_time
        
        print(f"WhatsApp Alert with Image Sent! Message SID: {message.sid}")
        print(f"Image attached: {image_path}")
        return True
        
    except Exception as e:
        print(f"WhatsApp Alert with Media Error: {str(e)}")
        return False

def send_custom_whatsapp(message_body):
    """
    Send custom WhatsApp alert with custom message
    """
    global last_whatsapp_time
    
    try:
        # Get Twilio WhatsApp credentials
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))
        whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', os.getenv('TWILIO_WHATSAPP_NUMBER'))
        to_whatsapp_number = getattr(settings, 'ALERT_WHATSAPP_NUMBER', os.getenv('ALERT_WHATSAPP_NUMBER'))
        
        if not all([account_sid, auth_token, whatsapp_number, to_whatsapp_number]):
            print("WhatsApp Alert Error: Missing Twilio WhatsApp credentials")
            return False
        
        current_time = time.time()
        
        # Spam prevention
        if current_time - last_whatsapp_time < WHATSAPP_COOLDOWN_PERIOD:
            print(f"WhatsApp Alert: Cooldown active ({WHATSAPP_COOLDOWN_PERIOD}s)")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send custom WhatsApp message
        message = client.messages.create(
            from_=f'whatsapp:{whatsapp_number}',
            body=message_body,
            to=f'whatsapp:{to_whatsapp_number}'
        )
        
        # Update last WhatsApp time
        last_whatsapp_time = current_time
        
        print(f"Custom WhatsApp Alert Sent! Message SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Custom WhatsApp Alert Error: {str(e)}")
        return False

def test_whatsapp_connection():
    """
    Test WhatsApp connection with a test message
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return send_custom_whatsapp(f"Test WhatsApp Alert - System Online at {timestamp}")
    except Exception as e:
        print(f"WhatsApp Test Error: {str(e)}")
        return False

# Configuration helper
def get_whatsapp_config_status():
    """
    Check if WhatsApp configuration is complete
    """
    config_status = {
        'twilio_account_sid': bool(getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))),
        'twilio_auth_token': bool(getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))),
        'twilio_whatsapp_number': bool(getattr(settings, 'TWILIO_WHATSAPP_NUMBER', os.getenv('TWILIO_WHATSAPP_NUMBER'))),
        'alert_whatsapp_number': bool(getattr(settings, 'ALERT_WHATSAPP_NUMBER', os.getenv('ALERT_WHATSAPP_NUMBER'))),
        'cooldown_period': WHATSAPP_COOLDOWN_PERIOD
    }
    
    all_configured = all(config_status.values())
    config_status['all_configured'] = all_configured
    
    return config_status
