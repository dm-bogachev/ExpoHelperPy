from multiprocessing import process
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread
import subprocess
import time
import os
from Config import Config

from database_handlers import get_user, update_user

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

if os.environ.get("DOCKER"):
    shared_data_path = "/shared_data/videos/raw"
else:
    shared_data_path = "../shared_data/videos/raw"
os.makedirs(shared_data_path, exist_ok=True)

app = FastAPI(
    root_path="/api/recorder",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    # lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# FFMPEG_CMD_TEMPLATE = [
#     "ffmpeg",
#     "-y",
#     "-color_range", "tv",
#     "-i", Config.get("video_url"),
#     "-vf", "scale=in_range=tv:out_range=tv,format=yuv420p",
#     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
#     "-colorspace", "bt709",
#     "-color_primaries", "bt709",
#     "-color_trc", "bt709",
#     "-color_range", "tv",
#     "-t", 10,
#     f"{shared_data_path}/raw_default.mp4"
# ]

recording_process = None
recording_thread = None
stop_flag = False

import signal
from datetime import datetime
import requests

def record_video(user_id, duration=None):
    Config.init()
    FFMPEG_CMD_TEMPLATE = [
    "ffmpeg",
    "-y",
    "-i", Config.get("video_url"),
    # "-vf", "scale=1920:1080",
    "-c:v", "copy",
    "-t", 10,
    f"{shared_data_path}/raw_default.mp4"
]
    global recording_process, stop_flag
    user = get_user(user_id)
    logger.debug(f"Retrieved user data: {user}")
    if not user:
        logger.error(f"User {user_id} not found")
        return
    chat_id = user.get("chat_id")
    if not chat_id and chat_id != 0:
        logger.error(f"Chat ID not found for user {user_id}")
        return
    update_user(user_id, {"status": 10})
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"{shared_data_path}/{user['id']}_video_{chat_id}_{timestamp}.mp4"
    logger.debug(f"Output file name: {output_name}")
    if duration:
        cmd = FFMPEG_CMD_TEMPLATE[:-2] + [str(duration), output_name]
    else:
        cmd = FFMPEG_CMD_TEMPLATE[:-2] + [output_name]
    logger.debug(f"Started recording process with command: {' '.join(cmd)}")


    recording_process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    # Send command to robot API to start

    try:
        response = requests.post(
            "http://expo-robot:8002/api/robot/send?command=START&expect_response=false",
            headers={"accept": "application/json"},
            data=""
        )
        logger.info(f"Robot command response: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Failed to send command to robot: {e}")

    try:
        while recording_process.poll() is None:
            if stop_flag:
                # Корректно завершаем ffmpeg
                try:
                    recording_process.stdin.write(b"q\n")
                    recording_process.stdin.flush()
                except Exception as e:
                    logger.error(f"Error sending 'q' to ffmpeg: {e}")
                recording_process.wait()
                logger.info("Recording stopped by user")
                break
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error while recording: {e}")
        if recording_process.poll() is None:
            recording_process.terminate()
            recording_process.wait()
    time.sleep(3) 
    update_user(user_id, {"status": 1, "recorded_file_name": output_name})
    

@app.post("/start")
def start_recording(user_id: int, duration: int = 0):
    logger.info(f"Starting recording for user {user_id} with duration {duration}")
    global recording_thread, stop_flag
    if recording_thread and recording_thread.is_alive():
        return {"status": "already recording"}
    stop_flag = False
    recording_thread = Thread(target=record_video, args=(user_id, duration if duration > 0 else None))
    recording_thread.start()

    return {"status": "recording started"}


@app.post("/stop")
def stop_recording():
    logger.info("Stopping recording")
    global stop_flag
    stop_flag = True
    return {"status": "recording stopped"}
