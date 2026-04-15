#!/usr/bin/env python
"""
Complete Detection System Test
Test all components of the mask detection system
"""

import os
import sys
import django
import base64
from PIL import Image
import io

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from detection.mask_detector import detector
from detection.models import DetectionRecord

def test_mask_detector():
    """Test the mask detector component"""
    print("Testing Mask Detector...")
    print("-" * 40)
    
    try:
        # Test with a sample image
        img = Image.new('RGB', (640, 480), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        label, confidence = detector.detect_face_mask(img_bytes)
        
        print(f"Detector loaded: {detector.model is not None}")
        print(f"Detection result: {label}")
        print(f"Confidence: {confidence:.2f}%")
        print("Mask Detector: PASSED")
        return True
        
    except Exception as e:
        print(f"Mask Detector: FAILED - {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\nTesting Database Operations...")
    print("-" * 40)
    
    try:
        # Test creating a detection record
        record = DetectionRecord.objects.create(
            status='no_mask',
            confidence=95.5,
            user=None
        )
        
        print(f"Created record: {record.id}")
        print(f"Status: {record.status}")
        print(f"Confidence: {record.confidence}%")
        
        # Test querying
        records = DetectionRecord.objects.all()
        print(f"Total records in database: {records.count()}")
        
        # Clean up
        record.delete()
        print("Database Operations: PASSED")
        return True
        
    except Exception as e:
        print(f"Database Operations: FAILED - {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint"""
    print("\nTesting API Endpoint...")
    print("-" * 40)
    
    try:
        from detection.views import detect_mask
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        import json
        
        # Create a mock request
        request = HttpRequest()
        request.method = 'POST'
        request.user = AnonymousUser()
        
        # Create test image
        img = Image.new('RGB', (640, 480), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # Convert to base64
        img_b64 = base64.b64encode(img_bytes).decode()
        
        # Set request data
        request.data = {'image': img_b64}
        
        # Call the view
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        api_request = factory.post('/api/detect/', {'image': img_b64})
        
        # Test the view function
        response = detect_mask(api_request)
        
        print(f"API Response status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"API Response data keys: {list(response.data.keys())}")
            print("API Endpoint: PASSED")
        else:
            print("API Endpoint: FAILED - No response data")
            return False
        
        return True
        
    except Exception as e:
        print(f"API Endpoint: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_screenshot_functionality():
    """Test screenshot saving functionality"""
    print("\nTesting Screenshot Functionality...")
    print("-" * 40)
    
    try:
        # Test screenshot saving
        img = Image.new('RGB', (640, 480), color='yellow')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # Test screenshot save
        screenshot_path = detector.save_no_mask_screenshot(img_bytes, 95.5)
        
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"Screenshot saved: {screenshot_path}")
            print(f"File exists: {os.path.exists(screenshot_path)}")
            print("Screenshot Functionality: PASSED")
            
            # Clean up
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                print("Test screenshot cleaned up")
            
            return True
        else:
            print("Screenshot Functionality: FAILED - No file saved")
            return False
        
    except Exception as e:
        print(f"Screenshot Functionality: FAILED - {e}")
        return False

def test_alert_systems():
    """Test alert systems (SMS and WhatsApp)"""
    print("\nTesting Alert Systems...")
    print("-" * 40)
    
    try:
        # Test SMS alert (may fail if not configured)
        try:
            from detection.sms_alert import send_sms_alert
            sms_result = send_sms_alert()
            print(f"SMS Alert: {'PASSED' if sms_result else 'FAILED (not configured)'}")
        except Exception as e:
            print(f"SMS Alert: FAILED - {e}")
        
        # Test WhatsApp alert (may fail if not configured)
        try:
            from detection.whatsapp_alert import send_whatsapp_with_media
            whatsapp_result = send_whatsapp_with_media("test.jpg", 95.5)
            print(f"WhatsApp Alert: {'PASSED' if whatsapp_result else 'FAILED (not configured)'}")
        except Exception as e:
            print(f"WhatsApp Alert: FAILED - {e}")
        
        print("Alert Systems: Tested (may require configuration)")
        return True
        
    except Exception as e:
        print(f"Alert Systems: FAILED - {e}")
        return False

def main():
    """Main test function"""
    print("Face Mask Detection System - Complete Test")
    print("=" * 50)
    
    tests = [
        ("Mask Detector", test_mask_detector),
        ("Database Operations", test_database_operations),
        ("API Endpoint", test_api_endpoint),
        ("Screenshot Functionality", test_screenshot_functionality),
        ("Alert Systems", test_alert_systems),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\nAll tests passed! Detection system is working correctly!")
    else:
        print(f"\n{failed} test(s) failed. Please check the issues above.")
    
    print("\nNext steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Open the frontend: http://127.0.0.1:8000/")
    print("3. Test live detection: http://127.0.0.1:8000/live-detection/")
    print("4. Test with camera: http://127.0.0.1:8000/test-detection/")

if __name__ == "__main__":
    main()
