from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.db.models import Count, Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta

import base64
import json
import csv
import time
import threading
from .models import DetectionRecord, SystemSettings
from .serializers import DetectionRecordSerializer, SystemSettingsSerializer
from django.conf import settings

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    return Response({'success': False, 'error': 'Invalid credentials'}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not username or not password:
        return Response({'success': False, 'error': 'Username and password are required'}, status=400)

    if confirm_password is not None and password != confirm_password:
        return Response({'success': False, 'error': 'Passwords do not match'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'success': False, 'error': 'Username already exists'}, status=400)

    if email:
        try:
            validate_email(email)
        except ValidationError:
            return Response({'success': False, 'error': 'Invalid email'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'success': False, 'error': 'Email already exists'}, status=400)

    user = User.create_user(username=username, email=email or '', password=password)
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }, status=201)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'success': True})

@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        })
    return Response({'authenticated': False})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def detect_mask(request):
    """Detect mask using local YOLO (best.pt)"""
    try:
        image_data = request.data.get('image')
        
        if not image_data:
            return Response({'error': 'No image provided'}, status=400)
        
        from .mask_detector import detector

        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        label, confidence = detector.detect_face_mask(image_bytes)
        mask_detected = label == 'with_mask'
        confidence = float(confidence) * 100 if confidence <= 1 else float(confidence)
        
        record_id = None
        screenshot_path = None
        
        # Auto Screenshot: Save image when no mask is detected
        if not mask_detected:
            screenshot_path = detector.save_no_mask_screenshot(image_bytes, confidence)
            print(f"Auto Screenshot Saved: {screenshot_path}")
            
            # Send SMS alert for no mask detection
            from .sms_alert import send_sms_alert
            sms_sent = send_sms_alert()
            if sms_sent:
                print(f"SMS Alert Sent for No Mask Detection")
            
            # Send WhatsApp alert (Twilio Production Standard)
            from .whatsapp_alert import send_whatsapp_with_media
            try:
                whatsapp_sent = send_whatsapp_with_media(screenshot_path, confidence)
                if whatsapp_sent:
                    print("Production WhatsApp alert sent successfully!")
                else:
                    print("WhatsApp alert skipped (cooldown or configuration missing)")
            except Exception as e:
                print(f"Production WhatsApp error: {e}")
        
        detection = DetectionRecord.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status='mask' if mask_detected else 'no_mask',
            confidence=confidence,
            image=screenshot_path if screenshot_path else None
        )
        record_id = detection.id
        
        return Response({
            'success': True,
            'mask_detected': mask_detected,
            'confidence': round(confidence, 2),
            'record_id': record_id,
            'screenshot_saved': screenshot_path is not None,
            'screenshot_path': screenshot_path,
            'authenticated': bool(request.user and request.user.is_authenticated),
            'user': request.user.username if (request.user and request.user.is_authenticated) else None,
        })
            
    except Exception as e:
        print(f"API error: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

class DetectionRecordViewSet(viewsets.ModelViewSet):
    serializer_class = DetectionRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return DetectionRecord.objects.filter(user=self.request.user)
        return DetectionRecord.objects.filter(user__isnull=True)
    
    def get_permissions(self):
        # Allow anonymous users to update records for action buttons
        if self.action == 'partial_update':
            return [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=None)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export detection records as CSV"""
        records = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="mask_detection_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Timestamp', 'Status', 'Confidence (%)', 'User'])
        
        for record in records:
            writer.writerow([
                record.id,
                record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                record.get_status_display(),
                round(record.confidence, 2),
                record.user.username if record.user else 'N/A'
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get detection statistics"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        mask_count = queryset.filter(status='mask').count()
        no_mask_count = queryset.filter(status='no_mask').count()
        
        # Today's stats
        today = datetime.now().date()
        today_records = queryset.filter(timestamp__date=today)
        today_count = today_records.count()
        
        # Last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        week_records = queryset.filter(timestamp__gte=week_ago)
        
        return Response({
            'total_detections': total,
            'mask_detected': mask_count,
            'no_mask_detected': no_mask_count,
            'today_count': today_count,
            'week_count': week_records.count(),
            'compliance_rate': round((mask_count / total * 100) if total > 0 else 0, 2)
        })

    @action(detail=False, methods=['get'])
    def no_mask_screenshots(self, request):
        """Get all no-mask detection records with screenshots"""
        # Get all no-mask records with actual images (ignore user filtering for this endpoint)
        queryset = DetectionRecord.objects.filter(
            status='no_mask', 
            image__isnull=False
        ).exclude(image='').order_by('-timestamp')
        
        screenshots_data = []
        for record in queryset:
            screenshot_info = {
                'id': record.id,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'confidence': round(record.confidence, 2),
                'image_url': record.image.url if record.image else None,
                'user': record.user.username if record.user else 'Anonymous'
            }
            screenshots_data.append(screenshot_info)
        
        return Response({
            'screenshots': screenshots_data,
            'total_count': len(screenshots_data)
        })

    @action(detail=False, methods=['get'])
    def download_screenshots(self, request):
        """Download all screenshots as ZIP file"""
        import zipfile
        import io
        
        queryset = DetectionRecord.objects.filter(
            status='no_mask', 
            image__isnull=False
        ).exclude(image='').order_by('-timestamp')
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for record in queryset:
                if record.image and record.image.path:
                    try:
                        # Add file to ZIP with timestamp in filename
                        timestamp = record.timestamp.strftime('%Y%m%d_%H%M%S')
                        filename_in_zip = f"no_mask_{timestamp}_{record.id}.jpg"
                        zip_file.write(record.image.path, filename_in_zip)
                    except Exception as e:
                        print(f"Error adding file {record.image.path}: {e}")
                        continue
        
        zip_buffer.seek(0)
        
        # Create response
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="no_mask_screenshots_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"'
        
        return response

def screenshots_view(request):
    """Display all no-mask screenshots"""
    from django.shortcuts import render
    return render(request, 'screenshots.html')

def screenshot_detail_view(request):
    """Display single screenshot details"""
    from django.shortcuts import render
    return render(request, 'screenshot_detail.html')

class SystemSettingsViewSet(viewsets.ModelViewSet):
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAuthenticated]
