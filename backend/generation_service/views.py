from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserMedia
from .serializers import UserMediaSerializer
import requests
from utils.permission import JWTAuth, JWTUtils

FASTAPI_URL = "http://127.0.0.1:9000/process-video/"


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
    

class GenerateVideo(APIView):
    """Handles video processing request and communicates with FastAPI"""
    permission_classes = [JWTAuth]

    def post(self, request):
        """
        Dummy function for storing video temporarly and feed to fastapi
        """
        user_id = JWTUtils.fetch_user_id(request)
        video_file = request.FILES.get("video") 

        if not video_file:
            return Response({"error": "No video file provided"}, status=400)

        video_path = f"media/uploads/{video_file.name}"
        with open(video_path, "wb+") as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        response = requests.post(FASTAPI_URL, data={"user_id": user_id, "video_path": video_path})

        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response({"error": "FastAPI processing failed"}, status=500)
        

class SaveVideoUrl(APIView):

    def post(self,request):
        user_id = request.data.get('user_id')
        video_url = request.data.get('video_url')

        """
        Save the video url to database
        """

        return Response({"message":"video url saved"},status=200)