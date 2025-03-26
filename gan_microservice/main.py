# main.py
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
import uuid
import os
import tempfile
import uvicorn
from image_processing import process_images, check_folder
from video_processing import Cartoonizer
from websocket_handler import websocket_endpoint

app = FastAPI()

DJANGO_API_URL = 'http://127.0.0.1:8000/api/gan/save-image/'
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

# Video Processing Endpoint
@app.post("/process-video/")
async def process_video(
    user_id: str = Form(...),
    video: UploadFile = File(...),
    model_path: str = Form(default=""),
    device: str = Form(default="cpu"),
    if_concat: str = Form(default="None"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    task_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, video.filename)
    output_dir = check_folder(f"output/{task_id}")

    with open(input_path, "wb") as f:
        f.write(await video.read())

    cartoonizer = Cartoonizer(input_path, model_path, device, output_dir, if_concat)
    background_tasks.add_task(cartoonizer.process, task_id, user_id)
    return {"message": "Video processing started", "task_id": task_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)