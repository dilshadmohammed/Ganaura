from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import asyncio
import boto3
import uuid
import os
import requests

app = FastAPI()

# DigitalOcean Spaces Configuration
DO_SPACES_REGION = "nyc3"  # Change based on your region
DO_SPACES_BUCKET = "your-bucket-name"
DO_SPACES_ENDPOINT = f"https://{DO_SPACES_REGION}.digitaloceanspaces.com"
DO_SPACES_ACCESS_KEY = "your-access-key"
DO_SPACES_SECRET_KEY = "your-secret-key"

# Create S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=DO_SPACES_ENDPOINT,
    aws_access_key_id=DO_SPACES_ACCESS_KEY,
    aws_secret_access_key=DO_SPACES_SECRET_KEY,
)


DJANGO_API_URL = "http://127.0.0.1:8000/api/update-progress/"
# Simulating a request from Django
DJANGO_SECRET_TOKEN = "your-secret-token"

async def generate_video(task_id, user_id):
    """Simulate AI video generation and notify Django"""
    for progress in [0, 25, 50, 75, 100]:
        await asyncio.sleep(2)  # Simulate processing time

        # Notify Django with user_id
        requests.post(DJANGO_API_URL, json={"user_id": user_id, "progress": progress})

@app.post("/process-video/")
async def process_video(user_id: int, background_tasks: BackgroundTasks):
    """Start video processing in background"""
    background_tasks.add_task(generate_video, "task_123", user_id)
    return {"message": "Processing started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
