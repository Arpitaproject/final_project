"""
Custom middleware to disable CSRF for specific API endpoints
"""
from django.utils.deprecation import MiddlewareMixin

class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """Disable CSRF check for API endpoints"""
    
    def process_request(self, request):
        # Disable CSRF for detection API
        if request.path.startswith('/api/detect'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
