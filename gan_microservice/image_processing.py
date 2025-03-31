# image_processing.py
import cv2
import numpy as np
import onnxruntime as ort
from glob import glob
import os
import shutil
import tempfile
import asyncio
from websocket_handler import active_connections

pic_form = ['.jpeg', '.jpg', '.png', '.JPEG', '.JPG', '.PNG']

def check_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

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
def filter(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Convert to grayscale
    edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, 
                                  cv2.ADAPTIVE_THRESH_MEAN_C, 
                                  cv2.THRESH_BINARY, 9, 10)  # Edge detection

    # Apply bilateral filtering for a smooth, cartoonish look
    color = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

    # Convert edges back to 3 channels and blend with the color image
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    filter_image = cv2.bitwise_and(color, edges_colored)

    return filter_image

def save_images(images, image_path, size):
    images = (np.squeeze(images) + 1.) / 2 * 255  # Convert from [-1,1] to [0,255]
    images = np.clip(images, 0, 255).astype(np.uint8)  # Ensure valid pixel range
    images = cv2.resize(images, size)  # Resize to original dimensions

    anime_image = filter(images)

    cv2.imwrite(image_path, cv2.cvtColor(anime_image, cv2.COLOR_RGB2BGR))


async def process_images(task_id, user_id, input_path, output_path, model_path="/home/advay/Desktop/gaaaannnnnnn/Ganaura/gan_microservice/models/generator.onnx", device="cpu"):
    print(f"Image processing started for user {user_id}, task {task_id}")
    
    try:
        if ort.get_device() == 'GPU' and device == "gpu":
            session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        else:
            session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        x = session.get_inputs()[0].name
        y = session.get_outputs()[0].name

        sample_image, shape = load_test_data(input_path, model_path)
        image_path = os.path.join(output_path, os.path.basename(input_path))
        fake_img = session.run(None, {x: sample_image})
        save_images(fake_img[0], image_path, (shape[1], shape[0]))
    
    except Exception as e:
        print(f"Error in process_images: {e}")
        websocket = active_connections.get(user_id)
        if websocket:
            await websocket.send_json({
                "error": str(e),
                "task_id": task_id,
            })