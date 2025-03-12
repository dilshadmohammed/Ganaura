from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserMedia
from .serializers import UserMediaSerializer
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
        video_file = request.FILES.get("file") 

        if not video_file:
            return Response({"error": "No file provided"}, status=400)

        # Save file using serializer
        serializer = UserMediaSerializer(data={"user_id": user_id, "file": video_file})
        if serializer.is_valid():
            media_instance = serializer.save()

            if media_instance.media_type == "video":
                # Send video to FastAPI for processing
                response = requests.post(FASTAPI_URL, data={
                    "user_id": user_id,
                    "video_path": media_instance.file.path
                })

                if response.status_code == 200:
                    return Response({"message": "Video uploaded and sent for processing", "media": serializer.data})
                else:
                    return Response({"error": "FastAPI processing failed"}, status=500)

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    
class SaveVideoUrl(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        video_url = request.data.get('video_url')

        print("Received user_id:", user_id)

        # Ensure user_id and video_url are provided
        if not user_id or not video_url:
            return Response({"error": "User ID and video URL are required"}, status=400)

        # Check if user_id exists in User model
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "User ID does not exist in the database"}, status=404)
        
        try:
            # Fetch the latest video uploaded by the user
            media_instance = UserMedia.objects.filter(user=user, media_type='video').latest('uploaded_at')
            media_instance.processed_video_url = video_url
            media_instance.save()
            return Response({"message": "Video URL saved successfully"}, status=200)
        except UserMedia.DoesNotExist:
            return Response({"error": "No uploaded video found for this user"}, status=404)