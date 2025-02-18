from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import UserMediaUploadView

urlpatterns = [
    path('upload/', UserMediaUploadView.as_view(), name='upload-media'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
