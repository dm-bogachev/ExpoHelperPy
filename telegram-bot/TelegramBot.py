import asyncio
import logging
import threading
from telegram import Update
from telegram.ext import CallbackQueryHandler, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from Config import Config
from bot_handlers import start, handle_message, check_subscription

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)


class TelegramBot(threading.Thread):
    def __init__(self):
        super().__init__()
        self.token = Config.get("telegram_bot_token") 
        logging.info("Initializing TelegramBot with token: %s", self.token)

        self.app = ApplicationBuilder().token(self.token).build()
        logging.info("Application object created.")
        self.setup_handlers()

    async def send_message(self, chat_id, text, reply_markup=None):
        """Отправляет сообщение в указанный чат."""
        logging.info("Sending message to chat_id=%s: %s", chat_id, text)
        await self.app.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        logging.info("Message sent to chat_id=%s", chat_id)

    def setup_handlers(self):
        logging.info("Setting up handlers...")
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CallbackQueryHandler(check_subscription, pattern="^/check_subscription$"))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        logging.info("Handlers setup completed.")

    def run(self):
        # Создаем новый event loop и сохраняем его как атрибут объекта
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        logging.info("Telegram Bot thread started. Running polling...")
        self.app.run_polling()
        logging.info("Polling stopped.")

if __name__ == "__main__":
    bot_thread = TelegramBot()
    bot_thread.start()
    # Основной поток может выполнять другие задачи, либо ждать завершения бота:
    bot_thread.join()