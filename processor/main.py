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

while True:
    users_with_status_1 = get_users_by_status(1)
    if users_with_status_1:
        for user in users_with_status_1:
            chat_id = user["chat_id"]
            file_path = f"{shared_data_path}/{user['id']}_video_{chat_id}.txt"
            with open(file_path, "wb") as f:
                f.write(os.urandom(100 * 1024 * 1024))
            logger.info(f"Created file {file_path} with 100MB of random data.")
            update_user(user["id"], {"status": 2, "video_link": user["video_link"], "chat_id": chat_id, "name": user["name"]})  # Обновляем статус на 2 после отправки видео
    else:
        logger.info("No users with status 1 found.")
    users_with_status_2 = get_users_by_status(2)
    if users_with_status_2:
        for user in users_with_status_2:
            chat_id = user["chat_id"]
            if upload_file(f"{shared_data_path}/{user['id']}_video_{chat_id}.txt", f'{user["id"]}_video_{chat_id}.txt'):
                video_link = get_file_url(f'{user["id"]}_video_{chat_id}.txt')
                logger.info(f"Video file for user {user['id']} ({user['name']}) uploaded successfully.")
                update_user(user["id"], {"status": 3, "video_link": video_link, "chat_id": chat_id, "name": user["name"]})  # Обновляем статус на 3 после отправки видео
    else:
        logger.info("No users with status 2 found.")
    sleep(10)
