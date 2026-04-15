from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

import base64
import csv

from .models import DetectionRecord, SystemSettings
from .serializers import DetectionRecordSerializer, SystemSettingsSerializer


# ================= LOGIN =================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    print("LOGIN ATTEMPT:", username)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username
            }
        })

    return Response({'success': False, 'error': 'Invalid credentials'}, status=400)


# ================= REGISTER =================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username & password required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=400)

    user = User.objects.create_user(username=username, password=password)

    return Response({'success': True})


# ================= LOGOUT =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'success': True})


# ================= DETECTION =================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def detect_mask(request):
    try:
        print("🔥 API HIT")

        image_data = request.data.get('image')

        if not image_data:
            return Response({'error': 'No image provided'}, status=400)

        from .mask_detector import detector

        if ',' in image_data:
            image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)

        print("✅ Image decoded")

        label, confidence = detector.detect_face_mask(image_bytes)

        print("👉 RESULT:", label, confidence)

        mask_detected = label == 'with_mask'

        confidence = float(confidence) * 100 if confidence <= 1 else float(confidence)

        screenshot_path = None

        # 🚨 NO MASK DETECTED
        if not mask_detected:
            print("🚨 NO MASK")

            screenshot_path = detector.save_no_mask_screenshot(image_bytes, confidence)

            print("📸 Screenshot:", screenshot_path)

            # WhatsApp
            try:
                from .whatsapp_alert import send_whatsapp_with_media
                send_whatsapp_with_media(screenshot_path, confidence)
                print("📲 WhatsApp Sent")
            except Exception as e:
                print("❌ WhatsApp Error:", e)

        # Save record
        detection = DetectionRecord.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status='mask' if mask_detected else 'no_mask',
            confidence=confidence,
            image=screenshot_path if screenshot_path else None
        )

        return Response({
            'success': True,
            'mask_detected': mask_detected,
            'confidence': round(confidence, 2),
            'screenshot_saved': screenshot_path is not None
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return Response({'error': str(e)}, status=500)


# ================= RECORD VIEWSET =================
class DetectionRecordViewSet(viewsets.ModelViewSet):
    serializer_class = DetectionRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return DetectionRecord.objects.filter(user=self.request.user)
        return DetectionRecord.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=None)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        records = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="records.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Time', 'Status', 'Confidence'])

        for r in records:
            writer.writerow([r.id, r.timestamp, r.status, r.confidence])

        return response

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    """Get current user information"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            }
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def screenshots_view(request):
    """Get all screenshots (no mask detections)"""
    try:
        records = DetectionRecord.objects.filter(
            status='no_mask',
            image__isnull=False
        ).exclude(image='').order_by('-timestamp')
        
        screenshots_data = []
        for record in records:
            screenshots_data.append({
                'id': record.id,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'confidence': record.confidence,
                'image_url': f'/media/{record.image}' if record.image else None,
                'user': record.user.username if record.user else 'Anonymous',
                'action_taken': record.action_taken if hasattr(record, 'action_taken') else False,
                'rejected': record.rejected if hasattr(record, 'rejected') else False,
                'rejection_reason': record.rejection_reason if hasattr(record, 'rejection_reason') else None
            })
        
        return Response({
            'success': True,
            'screenshots': screenshots_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def screenshot_detail_view(request):
    """Get screenshot details"""
    screenshot_id = request.GET.get('id')
    if not screenshot_id:
        return Response({
            'success': False,
            'error': 'Screenshot ID required'
        }, status=400)
    
    try:
        record = DetectionRecord.objects.get(id=screenshot_id)
        
        screenshot_data = {
            'id': record.id,
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'confidence': record.confidence,
            'image_url': f'/media/{record.image}' if record.image else None,
            'user': record.user.username if record.user else 'Anonymous',
            'status': record.status,
            'action_taken': record.action_taken if hasattr(record, 'action_taken') else False,
            'rejected': record.rejected if hasattr(record, 'rejected') else False,
            'rejection_reason': record.rejection_reason if hasattr(record, 'rejection_reason') else None
        }
        
        return Response({
            'success': True,
            'screenshot': screenshot_data
        })
        
    except DetectionRecord.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Screenshot not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

# ================= SETTINGS =================
class SystemSettingsViewSet(viewsets.ModelViewSet):
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAuthenticated]