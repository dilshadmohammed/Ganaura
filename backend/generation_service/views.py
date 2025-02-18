from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserMedia
from .serializers import UserMediaSerializer

class UserMediaUploadView(generics.ListCreateAPIView):
    """
    API endpoint to upload and retrieve user media (images/videos).
    """
    queryset = UserMedia.objects.all()
    serializer_class = UserMediaSerializer
    parser_classes = [MultiPartParser, FormParser]  # Handle file uploads

    def create(self, request, *args, **kwargs):
        """
        Handle file upload and save it to the media folder.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "File uploaded successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
