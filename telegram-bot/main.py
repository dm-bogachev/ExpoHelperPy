import logging
import threading

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from TelegramBot import TelegramBot
from time import sleep
from database_handlers import *
from texts import *
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

def queue_worker():
    while True:
        users_with_status_3 = get_users_by_status(3)
        if users_with_status_3:
            for user in users_with_status_3:
                chat_id = user["chat_id"]
                video_link = user["video_link"]
                if video_link:
                    logger.info(f"Sending video link to user {user['id']} ({user['name']}) in chat {chat_id}: {video_link}")

                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(button_subscribe_1, url=url_subscribe_1)],
                        [InlineKeyboardButton(button_subscribe_2, url=url_subscribe_2)],
                        [InlineKeyboardButton(button_subscribe_3, callback_data="/check_subscription")]
                    ])

                    future = asyncio.run_coroutine_threadsafe(
                        bot_thread.send_message(chat_id, ask_subscription_text, reply_markup=keyboard),
                        bot_thread.loop
                    )
                    future.result()  # Дождаться выполнения (или обработать исключение)
                    update_user(user["id"], {"status": 4, "video_link": user["video_link"], "chat_id": chat_id, "name": user["name"]})  # Обновляем статус на 4 после отправки видео
        else:
            logger.info("No users with status 3 found.")
        sleep(10)

if __name__ == "__main__":
    bot_thread = TelegramBot()
    worker = threading.Thread(target=queue_worker, daemon=True)
    worker.start()
    bot_thread.run()  # Бот блокирует поток, но очередь работает в фоне
