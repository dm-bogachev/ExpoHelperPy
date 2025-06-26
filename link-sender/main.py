import logging
import threading

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from time import sleep
from database_handlers import *
from texts import *

import asyncio

logger = logging.getLogger("link_sender")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)


bot = Bot(token=Config.get("telegram_bot_token"))

async def send_message(chat_id, text, reply_markup=None):
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def main():
    while True:
        try:
            logger.info("Scanning for users with status 3 (Uploaded)")
            users_with_status_3 = get_users_by_status(3)
            if users_with_status_3:
                logger.debug(f"Found {len(users_with_status_3)} users with status 3.")
                for user in users_with_status_3:
                    logger.debug(f"Processing user {user['id']} ({user['name']}) with chat_id {user['chat_id']}.")
                    chat_id = user["chat_id"]
                    video_link = user["video_link"]
                    if video_link:
                        logger.info(f"Sending video link to user {user['id']} ({user['name']}) in chat {chat_id}: {video_link}")

                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton(button_subscribe_1, url=url_subscribe_1)],
                            [InlineKeyboardButton(button_subscribe_2, url=url_subscribe_2)],
                            [InlineKeyboardButton(button_subscribe_3, callback_data="/check_subscription")]
                        ])
                        
                        await send_message(chat_id, ask_subscription_text, reply_markup=keyboard)
                        
                        update_user(user["id"], {"status": 4, "video_link": user["video_link"], "chat_id": chat_id, "name": user["name"]}) 
                        logger.debug(f"User {user['id']} ({user['name']}) updated to status 4")
            else:
                logger.info("No users with status 3 found.")
            sleep(2)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            sleep(10)

asyncio.run(main())