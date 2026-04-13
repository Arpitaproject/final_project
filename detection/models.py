from django.db import models
from django.contrib.auth.models import User

class DetectionRecord(models.Model):
    STATUS_CHOICES = [
        ('mask', 'Mask Detected'),
        ('no_mask', 'No Mask'),
    ]
    
    ACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Action Taken'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    confidence = models.FloatField()
    image = models.ImageField(upload_to='detections/', null=True, blank=True)
    action_taken = models.BooleanField(default=False)
    action_status = models.CharField(max_length=10, choices=ACTION_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.status} - {self.confidence}% - {self.timestamp}"

class SystemSettings(models.Model):
    voice_alerts_enabled = models.BooleanField(default=True)
    alert_threshold = models.FloatField(default=0.7)
    auto_record = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return "System Settings"
