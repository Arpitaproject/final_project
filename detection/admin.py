from django.contrib import admin
from .models import DetectionRecord, SystemSettings

@admin.register(DetectionRecord)
class DetectionRecordAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'status', 'confidence', 'user']
    list_filter = ['status', 'timestamp']
    search_fields = ['user__username']
    readonly_fields = ['timestamp']

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['voice_alerts_enabled', 'alert_threshold', 'auto_record']
