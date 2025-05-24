import logging
import threading
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import commands, handlers
from UserService import UserService

# Настройка логирования (если ещё не настроена в основном модуле)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class TelegramBot(threading.Thread):
    def __init__(self):
        super().__init__()
        Config.load()
        self.token = Config.get("telegram_bot_api_token") 
        logging.info("Initializing TelegramBot with token: %s", self.token)
        UserService.init()
        self.app = Application.builder().token(self.token).build()
        logging.info("Application object created.")
        self.setup_handlers()

    async def send_message(self, chat_id, text):
        """Отправляет сообщение в указанный чат."""
        logging.info("Sending message to chat_id=%s: %s", chat_id, text)
        await self.app.bot.send_message(chat_id=chat_id, text=text)
        logging.info("Message sent to chat_id=%s", chat_id)

    def setup_handlers(self):
        logging.info("Setting up handlers...")
        self.app.add_handler(CommandHandler("start", commands.start_command))
        self.app.add_handler(CommandHandler("ask_interest", commands.ask_interest_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text_message))
        self.app.add_handler(CallbackQueryHandler(handlers.handle_callback))
        logging.info("Handlers setup completed.")

    def run(self):
        # Создаем новый event loop и сохраняем его как атрибут объекта
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        logging.info("Telegram Bot thread started. Running polling...")
        self.app.run_polling()
        logging.info("Polling stopped.")

if __name__ == "__main__":
    from Config import Config
    Config.load()
    TOKEN = Config.get("telegram_bot_api_token")  # замените на реальный токен
    logging.info("Starting TelegramBot with token from configuration.")
    bot_thread = TelegramBot()
    bot_thread.start()
    # Основной поток может выполнять другие задачи, либо ждать завершения бота:
    bot_thread.join()