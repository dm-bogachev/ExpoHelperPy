from time import sleep
from s3loader import *
from Config import Config
import logging
import os
from database_handlers import *
import subprocess

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

if os.environ.get("DOCKER"):
    shared_data_path = "/shared_data/videos"
else:
    shared_data_path = "./shared_data/videos"
os.makedirs(shared_data_path, exist_ok=True)
os.makedirs(f"{shared_data_path}/raw", exist_ok=True)
os.makedirs(f"{shared_data_path}/output", exist_ok=True)

# ------------------------------------------------------
# Сюда добавим логику видеообработчика

while True:
    logger.info("Scanning for users with status 1 (Recorded)")
    users_with_status_1 = get_users_by_status(1)
    if users_with_status_1:
        logger.debug(f"Found {len(users_with_status_1)} users with status 1.")
        for user in users_with_status_1:
            logger.debug(f"Processing user {user['id']} ({user['name']}) with chat_id {user['chat_id']}.")
            chat_id = user["chat_id"]
            file_path = f"{shared_data_path}/output/{user['id']}_video_{chat_id}.mp4"
            input_path = f"{shared_data_path}/raw/{user['id']}_video_{chat_id}.mp4"
            os.makedirs(os.path.dirname(input_path), exist_ok=True)
            if os.path.exists(input_path):
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-y",
                    "-hwaccel", "cuda",
                    "-i", input_path,
                    "-vf", "scale=1920:1080,fps=25,format=yuv420p",
                    "-c:v", "h264_nvenc",
                    "-profile:v", "baseline",  # или "main" для большей совместимости
                    "-preset", "fast",
                    "-crf", "23",
                    "-movflags", "+faststart",
                    "-c:a", "aac",
                    "-strict", "experimental",
                    file_path
                ]
                try:
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    logger.info(f"Converted {input_path} to {file_path} (1920x1080, 25fps, x264).")
                except subprocess.CalledProcessError as e:
                    logger.error(f"ffmpeg failed for {input_path}: {e.stderr.decode()}")
            else:
                logger.warning(f"Input file {input_path} does not exist.")

            update_user(user["id"], {"status": 2, "video_link": user["video_link"], "chat_id": chat_id, "name": user["name"]}) 
    else:
        logger.info("No users with status 1 found.")
    sleep(10)
