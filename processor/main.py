from time import sleep
from s3loader import *
from Config import Config
import logging
import os
from database_handlers import *

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

# ------------------------------------------------------
# Сюда добавим логику видеообработчика

while True:
    users_with_status_1 = get_users_by_status(1)
    if users_with_status_1:
        for user in users_with_status_1:
            chat_id = user["chat_id"]
            file_path = f"{shared_data_path}/{user['id']}_video_{chat_id}.mp4"
            with open(f"{shared_data_path}/vidos.mp4", "rb") as src, open(file_path, "wb") as dst:
                dst.write(src.read())
            logger.info(f"Created file {file_path} with 100MB of random data.")
            update_user(user["id"], {"status": 2, "video_link": user["video_link"], "chat_id": chat_id, "name": user["name"]}) 
    else:
        logger.info("No users with status 1 found.")
    sleep(10)
