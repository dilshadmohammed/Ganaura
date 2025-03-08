import os
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def user_media_path(instance, filename):
    """Generate unique file paths based on media type"""
    ext = filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{ext}"

    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        return f'images/{unique_filename}'
    elif ext in ['mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv']:
        return f'videos/{unique_filename}'
    else:
        raise ValidationError("Unsupported file format.")

class UserMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="media_uploads")
    file = models.FileField(upload_to=user_media_path)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically determine if the uploaded file is an image or a video."""
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            self.media_type = 'image'
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv']:
            self.media_type = 'video'
        else:
            raise ValidationError("Unsupported file format.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.media_type} - {self.file.name}"
