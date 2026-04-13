from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import delete_views

router = DefaultRouter()
router.register(r'records', views.DetectionRecordViewSet, basename='record')
router.register(r'settings', views.SystemSettingsViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/user/', views.current_user, name='current-user'),
    path('detect/', views.detect_mask, name='detect-mask'),
    path('screenshots/', views.screenshots_view, name='screenshots'),
    path('screenshot/', views.screenshot_detail_view, name='screenshot-detail'),
    path('records/<int:pk>/delete_screenshot/', delete_views.delete_screenshot_view, name='delete-screenshot'),
]
