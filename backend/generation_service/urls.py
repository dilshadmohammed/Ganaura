from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import GenerateVideo,SaveMediaUrl,UserGallery

urlpatterns = [
    #path('upload/', UserMediaUploadView.as_view(), name='upload-media'),
    path("generate-video/", GenerateVideo.as_view(), name="generate_video"),
    path("save-media/",SaveMediaUrl.as_view(),name='save-video'),
    path("gallery/",UserGallery.as_view(), name='gallery')
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
