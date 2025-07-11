from time import sleep
from s3loader import *
from Config import Config

import os
from database_handlers import *

import logging
logger = logging.getLogger("s3_file_loader")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

if os.environ.get("DOCKER"):
    shared_data_path = "/shared_data/videos/output"
else:
    shared_data_path = "./shared_data/videos/output"
os.makedirs(shared_data_path, exist_ok=True)


while True:
    try:
        logger.info("Scanning for users with status 2 (Processed)")
        users_with_status_2 = get_users_by_status(2)
        
        if users_with_status_2:
            Config.init()
            logger.debug(f"Found {len(users_with_status_2)} users with status 2.")
        
            for user in users_with_status_2:
                logger.debug(f"Processing user {user['id']} ({user['name']}) with chat_id {user['chat_id']}.")
                user_id = user["id"]
                chat_id = user["chat_id"]

                input_path = user['processed_file_name']
                file_name = os.path.basename(input_path)

                output_path = f'videos/{file_name}'

                if upload_file(input_path, output_path):
                    user["video_link"] = get_file_url(output_path)
                    logger.info(f"Video link for user {user['id']} ({user['name']}): {user['video_link']}")
                    
                    update_user(user["id"], {"status": 3, "video_link": user["video_link"], "chat_id": chat_id, "name": user["name"]})  
                    logger.debug(f"User {user['id']} ({user['name']}) updated to status 3")
        
        else:
            logger.info("No users with status 2 found.")
        
        sleep(2)
    
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        sleep(10)
