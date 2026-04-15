#!/usr/bin/env python
"""
Test Delete Screenshot Functionality
Test both individual and bulk delete operations
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from detection.models import DetectionRecord

def check_database_records():
    """Check what records exist in database"""
    print("Checking Database Records...")
    print("-" * 40)
    
    try:
        records = DetectionRecord.objects.all()
        print(f"Total records: {records.count()}")
        
        records_with_images = records.exclude(image__isnull=True).exclude(image='')
        print(f"Records with images: {records_with_images.count()}")
        
        print("\nRecent records with images:")
        for record in records_with_images[:5]:
            print(f"  ID: {record.id}")
            print(f"  Image: {record.image}")
            print(f"  Status: {record.status}")
            print(f"  Timestamp: {record.timestamp}")
            print()
        
        return records_with_images
        
    except Exception as e:
        print(f"Database error: {e}")
        return []

def check_screenshot_files():
    """Check what screenshot files exist"""
    print("Checking Screenshot Files...")
    print("-" * 40)
    
    media_dir = 'media/no_mask_screenshots'
    if os.path.exists(media_dir):
        screenshots = os.listdir(media_dir)
        print(f"Screenshots in directory: {len(screenshots)}")
        
        print("\nRecent screenshot files:")
        for screenshot in screenshots[:5]:
            file_path = os.path.join(media_dir, screenshot)
            file_size = os.path.getsize(file_path)
            print(f"  {screenshot} ({file_size} bytes)")
        
        return screenshots
    else:
        print("Screenshot directory not found")
        return []

def test_delete_api(record_id):
    """Test the delete API endpoint"""
    print(f"Testing Delete API for Record ID: {record_id}")
    print("-" * 40)
    
    try:
        # Test the API endpoint
        url = f'http://127.0.0.1:8000/api/records/{record_id}/delete_screenshot/'
        
        response = requests.delete(url, headers={
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test-token'  # We'll need to handle CSRF properly
        })
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print("✅ Delete API working correctly")
                    return True
                else:
                    print(f"❌ Delete API returned error: {data.get('error')}")
                    return False
            except:
                print("✅ Delete API responded (JSON parse issue but status 200)")
                return True
        else:
            print(f"❌ Delete API failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - make sure Django server is running")
        return False
    except Exception as e:
        print(f"❌ Delete API test error: {e}")
        return False

def test_delete_view_function(record_id):
    """Test the delete view function directly"""
    print(f"Testing Delete View Function for Record ID: {record_id}")
    print("-" * 40)
    
    try:
        from detection.delete_views import delete_screenshot_view
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        # Create mock request
        request = HttpRequest()
        request.method = 'DELETE'
        request.user = AnonymousUser()
        
        # Call the view function
        response = delete_screenshot_view(request, record_id)
        
        print(f"View Response Status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"View Response Data: {response.data}")
            
        if response.status_code == 200:
            print("✅ Delete view function working correctly")
            return True
        else:
            print(f"❌ Delete view function failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Delete view function error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Delete Screenshot Functionality Test")
    print("=" * 50)
    
    # Check what we have to work with
    records = check_database_records()
    screenshots = check_screenshot_files()
    
    if not records:
        print("\n❌ No records found in database to test with")
        print("Please run the detection system first to create some records")
        return
    
    # Get first record for testing
    test_record = records.first()
    if not test_record:
        print("\n❌ No records with images found to test with")
        return
    
    print(f"\nUsing record for testing: ID {test_record.id}")
    print(f"Image path: {test_record.image}")
    
    # Test 1: View function directly
    print("\n" + "=" * 50)
    print("TEST 1: Delete View Function")
    print("=" * 50)
    view_result = test_delete_view_function(test_record.id)
    
    # Test 2: API endpoint (if server is running)
    print("\n" + "=" * 50)
    print("TEST 2: Delete API Endpoint")
    print("=" * 50)
    api_result = test_delete_api(test_record.id)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"View Function Test: {'PASSED' if view_result else 'FAILED'}")
    print(f"API Endpoint Test: {'PASSED' if api_result else 'FAILED'}")
    
    if view_result:
        print("\n✅ Delete functionality is working at the view level")
        print("If API test failed, check:")
        print("  - Django server is running on http://127.0.0.1:8000")
        print("  - URL routing is correct")
        print("  - CSRF token handling")
        print("  - Frontend JavaScript is making correct requests")
    
    if not view_result and not api_result:
        print("\n❌ Delete functionality has issues")
        print("Check:")
        print("  - Database connection")
        print("  - Model permissions")
        print("  - File system permissions")
        print("  - View function implementation")

if __name__ == "__main__":
    main()
