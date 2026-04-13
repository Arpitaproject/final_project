from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import DetectionRecord

@csrf_exempt
@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def delete_screenshot_view(request, pk):
    """Delete a specific screenshot - Optimized for speed"""
    if request.method == 'DELETE':
        try:
            record = DetectionRecord.objects.get(id=pk)
            
            # Get image path before deletion
            image_path = None
            if record.image and hasattr(record.image, 'path'):
                image_path = record.image.path
            
            # Delete database record first (faster)
            record.delete()
            
            # Delete image file asynchronously (non-blocking)
            if image_path:
                try:
                    import os
                    import threading
                    
                    def delete_file_async():
                        try:
                            if os.path.exists(image_path):
                                os.remove(image_path)
                        except Exception as e:
                            print(f"Async file delete error: {e}")
                    
                    # Start file deletion in background thread
                    thread = threading.Thread(target=delete_file_async, daemon=True)
                    thread.start()
                    
                except Exception as e:
                    print(f"Error starting async delete: {e}")
            
            from rest_framework.response import Response
            return Response({
                'success': True,
                'message': 'Screenshot deleted successfully',
                'deleted': True
            })
            
        except DetectionRecord.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Screenshot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'success': False,
            'error': 'Method not allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
