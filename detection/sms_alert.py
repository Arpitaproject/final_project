"""
SMS Alert System for No Mask Detection
Automatically sends SMS alerts when no mask is detected
"""

import time
import os
from datetime import datetime
from twilio.rest import Client
from django.conf import settings

# Global variable to prevent spam SMS
last_sms_time = 0
SMS_COOLDOWN_PERIOD = 15  # 15 seconds gap between SMS

def send_sms_alert():
    """
    Send SMS alert for no mask detection
    Includes spam prevention mechanism
    """
    global last_sms_time
    
    try:
        # Get Twilio credentials from environment variables or settings
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', os.getenv('TWILIO_PHONE_NUMBER'))
        to_number = getattr(settings, 'ALERT_PHONE_NUMBER', os.getenv('ALERT_PHONE_NUMBER'))
        
        # Check if all required credentials are available
        if not all([account_sid, auth_token, from_number, to_number]):
            print("SMS Alert Error: Missing Twilio credentials")
            return False
        
        current_time = time.time()
        
        # Spam prevention: Check if enough time has passed since last SMS
        if current_time - last_sms_time < SMS_COOLDOWN_PERIOD:
            print(f"SMS Alert: Cooldown active ({SMS_COOLDOWN_PERIOD}s)")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create timestamp for message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send SMS with timestamp and location info
        message = client.messages.create(
            body=f"! ALERT: No Mask Detected at {timestamp} - Hospital Security System",
            from_=from_number,
            to=to_number
        )
        
        # Update last SMS time
        last_sms_time = current_time
        
        print(f"SMS Alert Sent Successfully! Message SID: {message.sid}")
        print(f"Alert sent at: {timestamp}")
        return True
        
    except Exception as e:
        print(f"SMS Alert Error: {str(e)}")
        return False

def send_custom_alert(message_body):
    """
    Send custom SMS alert with custom message
    """
    global last_sms_time
    
    try:
        # Get Twilio credentials
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', os.getenv('TWILIO_PHONE_NUMBER'))
        to_number = getattr(settings, 'ALERT_PHONE_NUMBER', os.getenv('ALERT_PHONE_NUMBER'))
        
        if not all([account_sid, auth_token, from_number, to_number]):
            print("SMS Alert Error: Missing Twilio credentials")
            return False
        
        current_time = time.time()
        
        # Spam prevention
        if current_time - last_sms_time < SMS_COOLDOWN_PERIOD:
            print(f"SMS Alert: Cooldown active ({SMS_COOLDOWN_PERIOD}s)")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send custom SMS
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        # Update last SMS time
        last_sms_time = current_time
        
        print(f"Custom SMS Alert Sent! Message SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Custom SMS Alert Error: {str(e)}")
        return False

def test_sms_connection():
    """
    Test SMS connection with a test message
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return send_custom_alert(f"Test SMS Alert - System Online at {timestamp}")
    except Exception as e:
        print(f"SMS Test Error: {str(e)}")
        return False

# Configuration helper
def get_sms_config_status():
    """
    Check if SMS configuration is complete
    """
    config_status = {
        'twilio_account_sid': bool(getattr(settings, 'TWILIO_ACCOUNT_SID', os.getenv('TWILIO_ACCOUNT_SID'))),
        'twilio_auth_token': bool(getattr(settings, 'TWILIO_AUTH_TOKEN', os.getenv('TWILIO_AUTH_TOKEN'))),
        'twilio_phone_number': bool(getattr(settings, 'TWILIO_PHONE_NUMBER', os.getenv('TWILIO_PHONE_NUMBER'))),
        'alert_phone_number': bool(getattr(settings, 'ALERT_PHONE_NUMBER', os.getenv('ALERT_PHONE_NUMBER'))),
        'cooldown_period': SMS_COOLDOWN_PERIOD
    }
    
    all_configured = all(config_status.values())
    config_status['all_configured'] = all_configured
    
    return config_status
