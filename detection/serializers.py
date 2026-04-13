from rest_framework import serializers
from .models import DetectionRecord, SystemSettings
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class DetectionRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DetectionRecord
        fields = ['id', 'user', 'timestamp', 'status', 'confidence', 'image', 'action_taken', 'action_status', 'rejection_reason']
        read_only_fields = ['timestamp']

class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'
