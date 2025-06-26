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

logging.getLogger("httpx").setLevel(logging.WARNING)

bot_thread = TelegramBot()
bot_thread.run()  # Бот блокирует поток, но очередь работает в фоне
