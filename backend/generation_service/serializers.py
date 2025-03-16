from rest_framework import serializers
from .models import UserMedia
import uuid
from user.models import User

class UserMediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)  # Accept UUIDs # Accept user ID in API request
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserMedia
        fields = ['id', 'user_id', 'username', 'file', 'media_type', 'uploaded_at']
        read_only_fields = ['id', 'media_type', 'uploaded_at', 'username']

    def validate_file(self, value):
        """Validate the uploaded file type."""
        ext = value.name.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv']
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file format.")
        
        return value

    def create(self, validated_data):
        """Override create to assign the user and auto-detect media type."""
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)  # Fetch user from ID

        instance = UserMedia(user=user, **validated_data)
        instance.save()  # This will trigger the `save` method in models.py
        return instance
