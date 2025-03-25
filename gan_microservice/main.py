# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, Form
import asyncio
import boto3
from botocore.client import Config
import uuid
import os
import shutil
import tempfile
import cv2
import numpy as np
import onnxruntime as ort
from glob import glob
from typing import Dict
from pydantic import BaseModel
import uvicorn
from PIL import Image
import queue
import threading
import subprocess

app = FastAPI()

active_connections: Dict[str, WebSocket] = {}
DJANGO_API_URL = 'http://127.0.0.1:8000/api/gan/save-image/'
FASTAPI_SECRET = "absdfasasdfasf"

# ONNX Image Processing Functions
pic_form = ['.jpeg', '.jpg', '.png', '.JPEG', '.JPG', '.PNG']
video_form = ['.mp4', '.avi', '.mov', '.mkv']  # Supported video formats

def check_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# Image Processing Functions
def process_image(img, model_name):
    h, w = img.shape[:2]
    def to_8s(x):
        if 'tiny' in os.path.basename(model_name):
            return 256 if x < 256 else x - x % 16
        else:
            return 256 if x < 256 else x - x % 8
    img = cv2.resize(img, (to_8s(w), to_8s(h)))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 127.5 - 1.0
    return img

def load_test_data(image_path, model_name):
    img0 = cv2.imread(image_path).astype(np.float32)
    img = process_image(img0, model_name)
    img = np.expand_dims(img, axis=0)
    return img, img0.shape

def save_images(images, image_path, size):
    images = (np.squeeze(images) + 1.) / 2 * 255
    images = np.clip(images, 0, 255).astype(np.uint8)
    images = cv2.resize(images, size)
    cv2.imwrite(image_path, cv2.cvtColor(images, cv2.COLOR_RGB2BGR))

# Video Processing Classes (Adapted from your first script)
class Videocap:
    def __init__(self, video_path, model_name, limit=1280):
        self.model_name = model_name
        vid = cv2.VideoCapture(video_path)
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = vid.get(cv2.CAP_PROP_FPS)
        self.ori_width, self.ori_height = width, height

        max_edge = max(width, height)
        scale_factor = limit / max_edge if max_edge > limit else 1.
        height = int(round(height * scale_factor))
        width = int(round(width * scale_factor))
        self.width, self.height = self.to_8s(width), self.to_8s(height)

        self.count = 0
        self.cap = vid
        self.ret, frame = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.q = queue.Queue(maxsize=60)
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        while True:
            self.ret, frame = self.cap.read()
            if not self.ret:
                break
            frame = np.asarray(self.process_frame(frame, self.width, self.height))
            self.q.put(frame)
            self.count += 1
        self.cap.release()

    def read(self):
        f = self.q.get()
        self.q.task_done()
        return f

    def to_8s(self, x):
        if 'tiny' in self.model_name:
            return 256 if x < 256 else x - x % 16
        else:
            return 256 if x < 256 else x - x % 8

    def process_frame(self, img, width, height):
        img = Image.fromarray(img[:, :, ::-1]).resize((width, height), Image.Resampling.LANCZOS)
        img = np.array(img).astype(np.float32) / 127.5 - 1.0
        return np.expand_dims(img, axis=0)

class Cartoonizer:
    def __init__(self, video_path, model_path, device, output_dir, if_concat="None"):
        self.video_path = video_path
        self.model_path = model_path
        self.device = device
        self.output_dir = output_dir
        self.if_concat = if_concat
        if ort.get_device() == 'GPU' and self.device == "gpu":
            self.sess = ort.InferenceSession(self.model_path, providers=['CUDAExecutionProvider'])
        else:
            self.sess = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
        self.name = os.path.basename(self.model_path).rsplit('.', 1)[0]

    def post_process(self, img, wh):
        img = (img.squeeze() + 1.) / 2 * 255
        img = img.clip(0, 255).astype(np.uint8)
        img = Image.fromarray(img).resize((wh[0], wh[1]), Image.Resampling.LANCZOS)
        return np.array(img).astype(np.uint8)

    async def process(self, task_id, user_id):
        vid = Videocap(self.video_path, self.name)
        output_video_path = os.path.join(self.output_dir, f"{task_id}_{self.name}.mp4")
        output_video_sounds_path = os.path.join(self.output_dir, f"{task_id}_{self.name}_sounds.mp4")

        if self.if_concat == "Horizontal":
            video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), vid.fps, (vid.ori_width * 2, vid.ori_height))
        elif self.if_concat == "Vertical":
            video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), vid.fps, (vid.ori_width, vid.ori_height * 2))
        else:
            video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), vid.fps, (vid.ori_width, vid.ori_height))

        total_frames = vid.total
        for i in range(total_frames):
            if vid.count < total_frames and not vid.ret and vid.q.empty():
                video_writer.release()
                raise ValueError("The video is broken.")
            frame = vid.read()
            fake_img = self.sess.run(None, {self.sess.get_inputs()[0].name: frame})[0]
            fake_img = self.post_process(fake_img, (vid.ori_width, vid.ori_height))

            if self.if_concat == "Horizontal":
                fake_img = np.hstack((self.post_process(frame, (vid.ori_width, vid.ori_height)), fake_img))
            elif self.if_concat == "Vertical":
                fake_img = np.vstack((self.post_process(frame, (vid.ori_width, vid.ori_height)), fake_img))

            video_writer.write(fake_img[:, :, ::-1])

            # Send progress update via WebSocket
            progress = int((i + 1) / total_frames * 100)
            websocket = active_connections.get(user_id)
            if websocket:
                await websocket.send_json({
                    "progress": progress,
                    "task_id": task_id,
                    "processed_frame": i + 1
                })
            await asyncio.sleep(0.01)  # Small delay for WebSocket updates

        video_writer.release()

        try:
            sound_path = os.path.join(self.output_dir, "sound.mp3")
            subprocess.check_call(["ffmpeg", "-loglevel", "error", "-i", self.video_path, "-y", sound_path])
            subprocess.check_call(["ffmpeg", "-loglevel", "error", "-i", sound_path, "-i", output_video_path, "-y", "-c:v", "libx264", "-c:a", "copy", "-crf", "25", output_video_sounds_path])
            return output_video_sounds_path
        except:
            print("FFmpeg failed, returning silent video.")
            return output_video_path

# Existing Image Processing Function
async def process_images(task_id, user_id, input_imgs_path, output_path, model_path="model path here", device="cpu"):#give model path here
    print(f"Image processing started for user {user_id}, task {task_id}")
    temp_dir = tempfile.mkdtemp()
    result_dir = check_folder(os.path.join(temp_dir, "output"))
    
    try:
        test_files = glob(f'{input_imgs_path}/*.*')
        test_files = [x for x in test_files if os.path.splitext(x)[-1] in pic_form]
        
        if not test_files:
            raise ValueError("No valid images found in the input directory.")
        
        if ort.get_device() == 'GPU' and device == "gpu":
            session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        else:
            session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        x = session.get_inputs()[0].name
        y = session.get_outputs()[0].name
        
        total_files = len(test_files)
        for i, sample_file in enumerate(test_files):
            sample_image, shape = load_test_data(sample_file, model_path)
            image_path = os.path.join(result_dir, os.path.basename(sample_file))
            fake_img = session.run(None, {x: sample_image})
            save_images(fake_img[0], image_path, (shape[1], shape[0]))
            
            progress = int((i + 1) / total_files * 100)
            websocket = active_connections.get(user_id)
            if websocket:
                await websocket.send_json({
                    "progress": progress,
                    "task_id": task_id,
                    "processed_image": os.path.basename(sample_file)
                })
            await asyncio.sleep(0.1)
    
    except Exception as e:
        print(f"Error in process_images: {e}")
        websocket = active_connections.get(user_id)
        if websocket:
            await websocket.send_json({
                "error": str(e),
                "task_id": task_id,
            })
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# WebSocket Endpoint
@app.websocket("/ws/progress/")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user_id = "test_user"  # Replace with JWTUtils.fetch_user_id_ws(token) if using JWT
    if not user_id:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.pop(user_id, None)

# Image Processing Endpoint
class ImageRequest(BaseModel):
    user_id: str
    input_imgs_dir: str
    model_path: str = ""#give model path here
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
    image: UploadFile = File(...),
    model_path: str = Form(default=""),#give model path here
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
    model_path: str = Form(default=""),#give model path here
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