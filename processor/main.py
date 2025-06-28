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
    try:
        logger.info("Scanning for users with status 1 (Recorded)")
        users_with_status_1 = get_users_by_status(1)
        if users_with_status_1:
            Config.init()
            logger.debug(f"Found {len(users_with_status_1)} users with status 1.")
            for user in users_with_status_1:
                logger.debug(f"Processing user {user['id']} ({user['name']}) with chat_id {user['chat_id']}.")
                chat_id = user["chat_id"]
                
                input_path = user["recorded_file_name"]
                file_name = os.path.basename(input_path)
                
                output_path = f"{shared_data_path}/output/{file_name}"
                
                if os.path.exists(input_path):

                    update_user(user["id"], {"status": 20,})
                    # Get cut start/end from config
                    cut_start = Config.get("video_cut_start", 0)
                    cut_end = Config.get("video_cut_end", 1000)
                    duration = cut_end - cut_start

                    audio_enabled = Config.get("audio", True)
                    audio_path = Config.get("audio_path", "/shared_data/audio.mp3")
                    watermark_path = Config.get("watermark_path", "/shared_data/watermark.png")

                    if Config.get("watermark", True) and os.path.exists(watermark_path):
                        
                        if audio_enabled and os.path.exists(audio_path):
                            ffmpeg_cmd = [
                                "ffmpeg",
                                "-y",
                                "-hwaccel", "cuda",
                                "-ss", str(cut_start),
                                "-i", input_path,
                                "-t", str(duration),
                                "-i", watermark_path,
                                "-i", audio_path,
                                "-filter_complex", "[1:v]format=rgba,colorchannelmixer=aa=0.5[wm];[0:v][wm]overlay=W-w-20:H-h-20,scale=1920:1080,fps=25,format=yuv420p[v]",
                                "-map", "[v]",
                                "-map", "2:a",
                                "-c:v", "h264_nvenc",
                                "-profile:v", "baseline",
                                "-preset", "fast",
                                "-crf", "23",
                                "-movflags", "+faststart",
                                "-c:a", "aac",
                                "-shortest",
                                output_path
                            ]
                        else:
                            ffmpeg_cmd = [
                                "ffmpeg",
                                "-y",
                                "-hwaccel", "cuda",
                                "-ss", str(cut_start),
                                "-i", input_path,
                                "-t", str(duration),
                                "-i", watermark_path,
                                "-filter_complex", "[1:v]format=rgba,colorchannelmixer=aa=0.5[wm];[0:v][wm]overlay=W-w-20:H-h-20,scale=1920:1080,fps=25,format=yuv420p",
                                "-c:v", "h264_nvenc",
                                "-profile:v", "baseline",
                                "-preset", "fast",
                                "-crf", "23",
                                "-movflags", "+faststart",
                                "-c:a", "aac",
                                "-strict", "experimental",
                                output_path
                            ]
                    else:
                        if audio_enabled and os.path.exists(audio_path):
                            ffmpeg_cmd = [
                                "ffmpeg",
                                "-y",
                                "-hwaccel", "cuda",
                                "-ss", str(cut_start),
                                "-i", input_path,
                                "-t", str(duration),
                                "-i", audio_path,
                                "-vf", "scale=1920:1080,fps=25,format=yuv420p",
                                "-map", "0:v",
                                "-map", "1:a",
                                "-c:v", "h264_nvenc",
                                "-profile:v", "baseline",
                                "-preset", "fast",
                                "-crf", "23",
                                "-movflags", "+faststart",
                                "-c:a", "aac",
                                "-shortest",
                                output_path
                            ]
                        else:
                            ffmpeg_cmd = [
                                "ffmpeg",
                                "-y",
                                "-hwaccel", "cuda",
                                "-ss", str(cut_start),
                                "-i", input_path,
                                "-t", str(duration),
                                "-vf", "scale=1920:1080,fps=25,format=yuv420p",
                                "-c:v", "h264_nvenc",
                                "-profile:v", "baseline",
                                "-preset", "fast",
                                "-crf", "23",
                                "-movflags", "+faststart",
                                "-c:a", "aac",
                                "-strict", "experimental",
                                output_path
                            ]
                    try:
                        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        logger.info(f"Converted {input_path} to {output_path} (1920x1080, 25fps, x264).")
                    except subprocess.CalledProcessError as e:
                        logger.error(f"ffmpeg failed for {input_path}: {e.stderr.decode()}")
                else:
                    logger.warning(f"Input file {input_path} does not exist.")

                update_user(user["id"], {"status": 2, "processed_file_name": output_path}) 
        else:
            logger.info("No users with status 1 found.")
        sleep(2)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        sleep(10)
