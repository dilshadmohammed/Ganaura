from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CloudMedia, UserMedia
from .serializers import UserMediaSerializer,CloudMediaSerializer
import requests
from utils.permission import JWTAuth, JWTUtils
from user.models import User
from .models import UserMedia

FASTAPI_URL = "http://127.0.0.1:9000/process-video/"


# class UserMediaUploadView(generics.ListCreateAPIView):
#     """
#     API endpoint to upload and retrieve user media (images/videos).
#     """
#     queryset = UserMedia.objects.all()
#     serializer_class = UserMediaSerializer
#     parser_classes = [MultiPartParser, FormParser]  # Handle file uploads

#     def create(self, request, *args, **kwargs):
#         """
#         Handle file upload and save it to the media folder.
#         """
#         serializer = self.get_serializer(data=request.data)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "File uploaded successfully!", "data": serializer.data},
#                 status=status.HTTP_201_CREATED
#             )
        
#         return Response(serializer.err status=status.HTTP_400_BAD_REQUEST)
    


FASTAPI_URL = "http://127.0.0.1:9000/process-video/"


class GenerateVideo(APIView):
    """Handles media upload and video processing requests"""
    permission_classes = [JWTAuth]

    def post(self, request):
        """
        Handles media upload and sends videos to FastAPI
        """
        user_id = JWTUtils.fetch_user_id(request)  # Fetch user ID from JWT
        file = request.FILES.get("file") 


        # Save file using serializer
        serializer = UserMediaSerializer(data={"user_id": user_id, "file": file})
        if serializer.is_valid():
            media_instance = serializer.save()
            response = requests.post(FASTAPI_URL, data={
                "user_id": user_id,
                "media_path": f'http://localhost:8000/api/gan{media_instance.file.url}',
                "media_type" : media_instance.media_type
            })

            if response.status_code == 200:
                return Response({"message": "Video uploaded and sent for processing", "media": serializer.data})
            else:
                return Response({"error": "FastAPI processing failed"}, status=500)

        return Response(serializer.errors, status=400)
    
class SaveMediaUrl(APIView):
    def post(self, request):
        serializer = CloudMediaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Video URL saved successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserGallery(APIView):
    authentication_classes = [JWTAuth]

    def get(self, request):
        user = JWTUtils.fetch_user_id(request)
        media_type = request.query_params.get("media_type")  # Get media_type from query params

        if not media_type:  # Return error if media_type is missing
            return Response(
                {"error": "media_type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cloud_media_entries = CloudMedia.objects.filter(user_media__user=user, media_type=media_type)

        serializer = CloudMediaSerializer(cloud_media_entries, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
  
    def delete(self, request):

        user_id = JWTUtils.fetch_user_id(request)
        media_id = request.data.get("id") 

        if not media_id:
            return Response({"error": "Media ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cloud_media = CloudMedia.objects.get(id=media_id, user_media__user_id=user_id)
            cloud_media.delete()

            # Add logic to delete from the cloud
            
            return Response({"message": "Media deleted successfully"}, status=status.HTTP_200_OK)

        except CloudMedia.DoesNotExist:
            return Response({"error": "Media not found or does not belong to the user"}, status=status.HTTP_404_NOT_FOUND)
