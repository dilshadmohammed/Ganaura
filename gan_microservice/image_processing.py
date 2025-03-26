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

def save_images(images, image_path, size):
    images = (np.squeeze(images) + 1.) / 2 * 255
    images = np.clip(images, 0, 255).astype(np.uint8)
    images = cv2.resize(images, size)
    cv2.imwrite(image_path, cv2.cvtColor(images, cv2.COLOR_RGB2BGR))

async def process_images(task_id, user_id, input_imgs_path, output_path, model_path="model path here", device="cpu"):
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