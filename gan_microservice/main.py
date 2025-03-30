# main.py
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
import uuid
import os
import tempfile
import requests
import uvicorn
from image_processing import process_images, check_folder
from video_processing import Cartoonizer
from websocket_handler import websocket_endpoint
import asyncio
import aiohttp
import mimetypes

app = FastAPI()

DJANGO_API_URL = 'http://127.0.0.1:8000/api/gan/save-media/'
FASTAPI_SECRET = "absdfasasdfasf"

# WebSocket Endpoint
app.websocket("/ws/progress/")(websocket_endpoint)

# Image Processing Endpoint
class ImageRequest(BaseModel):
    user_id: str
    input_imgs_dir: str
    model_path: str = ""
    device: str = "cpu"

@app.post("/process-images/")
async def process_images_endpoint(request: ImageRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    output_path = f"output/{task_id}"
    background_tasks.add_task(process_images, task_id, request.user_id, request.input_imgs_dir, output_path, request.model_path, request.device)
    return {"message": "Image processing started", "task_id": task_id}

# Single Image Upload Endpoint
@app.post("/process-single-image/")
async def process_single_image(
    user_id: str = Form(...),
    image: UploadFile = File(""),
    model_path: str = Form(default=""),
    device: str = Form(default="cpu"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    task_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, image.filename)
    output_path = os.path.join(temp_dir, "output")
    
    with open(input_path, "wb") as f:
        f.write(await image.read())
    
    background_tasks.add_task(process_images, task_id, user_id, temp_dir, output_path, model_path, device)
    return {"message": "Single image processing started", "task_id": task_id}

@app.post("/process-video/")
async def generate_media(background_tasks: BackgroundTasks, user_id: str = Form(...), media_path: str = Form(...)):
    """
    Download media from URL, detect type, and notify WebSocket clients
    
    Args:
        task_id (str): Unique identifier for the task
        user_id (str): User identifier
        media_path (str): URL of the media to download
    """
    task_id = uuid.uuid4()
    model_path = '/home/dilshad/Desktop/Ganaura/gan_microservice/Ganaura_test.onnx'
    print(f"Media processing started for task {task_id}")
    
    try:
        # Determine file extension and create a unique filename
        file_extension = os.path.splitext(media_path)[-1]
        if not file_extension:
            # If no extension, try to get from content type
            async with aiohttp.ClientSession() as session:
                async with session.head(media_path) as response:
                    content_type = response.headers.get('Content-Type', '')
                    file_extension = mimetypes.guess_extension(content_type) or ''
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        download_path = os.path.join("downloads", unique_filename)
        
        # Ensure downloads directory exists
        os.makedirs("downloads", exist_ok=True)
        os.makedirs("generation_outputs", exist_ok=True)
        output_dir = 'generation_outputs'
        
        # Download the media
        async with aiohttp.ClientSession() as session:
            async with session.get(media_path) as response:
                # Validate response
                if response.status != 200:
                    raise Exception(f"Failed to download media. Status code: {response.status}")
                
                # Detect media type
                content_type = response.headers.get('Content-Type', '')
                media_type = 'image' if content_type.startswith('image/') else 'video' if content_type.startswith('video/') else 'unknown'
                
                # Stream download
                with open(download_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

        if media_type == 'image':
            background_tasks.add_task(process_images, task_id, user_id, download_path, output_dir, model_path, 'gpu')
        elif media_type == 'video':
            cartoonizer = Cartoonizer(download_path, model_path, 'gpu', output_dir, None)
            background_tasks.add_task(cartoonizer.process, task_id, user_id)


        # response = requests.post(
        #     DJANGO_API_URL,
        #     headers={"FastAPI-Secret": FASTAPI_SECRET},
        #     json={
        #         "user_id": user_id,
        #         "media_type": media_type,
        #         "media_url": f"downloads/{unique_filename}",
        #         "task_id": task_id
        #     }
        # )
        
        print(f"Media processing completed for task {task_id}")
        return {
            "success": True,
            "media_type": media_type,
            "file_path": download_path
        }
    
    except Exception as e:
        print(f"Error in media processing: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)