from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from detection import frontend_views

urlpatterns = [
    path('', frontend_views.login_page, name='login'),
    path('signup/', frontend_views.signup_page, name='signup'),
    path('dashboard/', frontend_views.dashboard_page, name='dashboard'),
    path('live-detection/', frontend_views.live_detection_page, name='live-detection'),
    path('records/', frontend_views.records_page, name='records'),
    path('test-detection/', frontend_views.test_detection_page, name='test-detection'),
    path('screenshots/', frontend_views.screenshots_view, name='screenshots'),
    path('admin/', admin.site.urls),
    path('api/', include('detection.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
