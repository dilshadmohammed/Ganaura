from rest_framework import serializers
from .models import CloudMedia, UserMedia
import uuid
from user.models import User

class UserMediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    user_id = serializers.CharField(write_only=True)  # Accept UUIDs # Accept user ID in API request
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


class CloudMediaSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True)
    media_url = serializers.URLField(required=True)
    media_type = serializers.ChoiceField(choices=UserMedia.MEDIA_TYPE_CHOICES, required=True)

    class Meta:
        model = CloudMedia
        fields = ['id','user_id', 'media_url', 'media_type']
        read_only_fields = ['id']

    def validate_user_id(self, value):
        """Check if user exists."""
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("User ID does not exist in the database.")
        return value

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        media_url = validated_data.pop('media_url')
        media_type = validated_data.pop('media_type')

        try:
            # Get the latest uploaded video for the user
            user = User.objects.get(pk=user_id)
            media_instance = UserMedia.objects.filter(user=user, media_type=media_type).latest('uploaded_at')

            # Get or create the related CloudMedia instance
            cloud_media_instance, created = CloudMedia.objects.get_or_create(user_media=media_instance)
            cloud_media_instance.media_url = media_url
            cloud_media_instance.media_type = media_type
            cloud_media_instance.save()

            return cloud_media_instance
        except UserMedia.DoesNotExist:
            raise serializers.ValidationError("No uploaded video found for this user.")