from fastapi import FastAPI, Request, HTTPException, BackgroundTasks,Form,WebSocket, WebSocketDisconnect, Depends
import asyncio
import boto3
import uuid
import os
import requests
from typing import Dict

from utils import JWTUtils


app = FastAPI()

active_connections: Dict[str, WebSocket] = {}
DJANGO_API_URL = 'http://127.0.0.1:8000/api/gan/save-video/'
FASTAPI_SECRET = "absdfasasdfasf"

@app.websocket("/ws/progress/")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection secured with JWT"""
    token = websocket.query_params.get("token")
    user_id = JWTUtils.fetch_user_id_ws(token)
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


async def generate_video(task_id, user_id):
    """Simulate AI video generation and notify WebSocket clients"""
    print("Video processing started")

    for progress in [0, 25, 50, 75, 100]:
        await asyncio.sleep(3)

        websocket = active_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_json({
                    "progress": progress,
                    "task_id": task_id,
                })
            except Exception as e:
                print(f"Error sending WebSocket update: {e}")
        else:
            print(f"User {user_id} is not connected.")
    
    requests.post(DJANGO_API_URL,headers={"FastAPI-Secret": FASTAPI_SECRET},json={"user_id": user_id,"video_url":"hello.com"})

@app.post("/process-video/")
async def process_video(background_tasks: BackgroundTasks, user_id: str = Form(...), video_path: str = Form(...)):
    """Start video processing in background"""
    background_tasks.add_task(generate_video, "task_123", user_id)
    return {"message": "Processing started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
