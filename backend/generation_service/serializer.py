from rest_framework import serializers
from .models import UserMedia

class UserMediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = UserMedia
        fields = ['id', 'file', 'media_type', 'uploaded_at']
        read_only_fields = ['id', 'media_type', 'uploaded_at']

    def validate_file(self, value):
        """Validate the uploaded file type."""
        ext = value.name.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv']
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file format.")
        
        return value

    def create(self, validated_data):
        """Override create to auto-detect media type."""
        instance = UserMedia(**validated_data)
        instance.save()  # This will trigger the `save` method in models.py
        return instance
