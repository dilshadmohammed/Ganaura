# video_processing.py
import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image
import queue
import threading
import os
import asyncio
import subprocess
import requests
from websocket_handler import active_connections
from s3api import upload_to_cloud

DJANGO_API_URL = 'http://127.0.0.1:8000/api/gan/save-media/'
FASTAPI_SECRET = "absdfasasdfasf"

video_form = ['.mp4', '.avi', '.mov', '.mkv']

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
    
    def filter(self, image):
        # Ensure image is uint8
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)

        # Remove batch dimension if present (e.g., (1, height, width, channels) -> (height, width, channels))
        if len(image.shape) == 4 and image.shape[0] == 1:
            image = image.squeeze(0)  # or image[0]

        # Check the number of channels
        if len(image.shape) == 2:  # Grayscale image (height, width)
            gray = image
        elif len(image.shape) == 3 and image.shape[2] in [3, 4]:  # RGB or RGBA
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            raise ValueError(f"Unsupported image shape: {image.shape}")

        # Apply edge detection
        edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, 
                                    cv2.ADAPTIVE_THRESH_MEAN_C, 
                                    cv2.THRESH_BINARY, 9, 10)

        # If input was grayscale, convert it to 3-channel for bilateral filter
        if len(image.shape) == 2:
            color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            color = image

        # Apply bilateral filter
        color = cv2.bilateralFilter(color, d=9, sigmaColor=75, sigmaSpace=75)

        # Convert edges to 3-channel for bitwise operation
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # Combine color image with edges
        filter_image = cv2.bitwise_and(color, edges_colored)

        return filter_image

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
            
            filtered_frame = self.filter(frame)
            
            fake_img = self.sess.run(None, {self.sess.get_inputs()[0].name: frame})[0]
            fake_img = self.post_process(fake_img, (vid.ori_width, vid.ori_height))
            
            filtered_fake_img = self.filter(fake_img)

            if self.if_concat == "Horizontal":
                
                combined_img = np.hstack((filtered_frame, filtered_fake_img))
            elif self.if_concat == "Vertical":
                combined_img = np.vstack((filtered_frame, filtered_fake_img))
            else:
                combined_img = filtered_fake_img

            video_writer.write(combined_img[:, :, ::-1])

            progress = int((i + 1) / total_frames * 100)
            websocket = active_connections.get(user_id)
            if websocket:
                await websocket.send_json({
                    "progress": progress,
                    "task_id": str(task_id),
                })
            await asyncio.sleep(0.01)

        video_writer.release()
        try:
            sound_path = os.path.join(self.output_dir, "sound.mp3")
            subprocess.check_call(["ffmpeg", "-loglevel", "error", "-i", self.video_path, "-y", sound_path])
            subprocess.check_call(["ffmpeg", "-loglevel", "error", "-i", sound_path, "-i", output_video_path, "-y", "-c:v", "libx264", "-c:a", "copy", "-crf", "25", output_video_sounds_path])
            final = output_video_sounds_path
        except:
            print("FFmpeg failed, returning silent video.")
            final = output_video_path
                
        media_url = upload_to_cloud(final)
        response = requests.post(
            DJANGO_API_URL,
            headers={"FastAPI-Secret": FASTAPI_SECRET},
            json={
                "user_id": user_id,
                "media_type": 'video',
                "media_url": media_url,
            }
        )
        self.cleanup_files(self.video_path, output_video_path, sound_path, output_video_sounds_path)
                
        return media_url
        
        
    def cleanup_files(self, input_video_path, output_video_path, sound_path, output_video_sounds_path):
        """
        Clean up temporary and intermediate files.
        
        Args:
            input_video_path (str): Path to the original input video
            output_video_path (str): Path to the output video without sound
            sound_path (str): Path to the extracted sound file
            output_video_sounds_path (str): Path to the output video with sound
        """
        files_to_delete = [
            input_video_path,  # Delete input video from downloads folder
            output_video_path,  # Delete output video without sound
            sound_path,  # Delete extracted sound file
        ]

        # If a video with sound was created, delete it as well
        if output_video_sounds_path != output_video_path:
            files_to_delete.append(output_video_sounds_path)

        # Attempt to delete each file
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

