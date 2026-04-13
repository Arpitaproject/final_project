from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import DetectionRecord
from django.db.models import Count
from datetime import datetime, timedelta
import json

def screenshots_view(request):
    """Display all no-mask screenshots"""
    return render(request, 'screenshots.html')

@ensure_csrf_cookie
def login_page(request):
    return render(request, 'frontend/login.html')

@ensure_csrf_cookie
def signup_page(request):
    return render(request, 'frontend/signup.html')

@ensure_csrf_cookie
def dashboard_page(request):
    return render(request, 'frontend/dashboard.html')

@ensure_csrf_cookie
def live_detection_page(request):
    return render(request, 'frontend/live-detection.html')

@ensure_csrf_cookie
def records_page(request):
    return render(request, 'frontend/records.html')

@ensure_csrf_cookie
def test_detection_page(request):
    return render(request, 'frontend/test-detection.html')
