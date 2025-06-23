from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from texts import *
from database_handlers import *
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    chat_id = update.effective_chat.id

    user_data = {
        "chat_id": chat_id,
        "status": -1,
        "video_link": None,
        "name": None 
    }
    add_user(user_data)
    logger.info(f"Added new user: {chat_id}")

    """Send a message when the command /start is issued."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)
    logger.info("Waiting for user's name input...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = get_users_by_chat_id(chat_id)
    if users and users[-1]["name"] is None:
        update_user(users[-1]["id"], {"name": update.message.text, "status": 0, "video_link": None, "chat_id": chat_id})
        await context.bot.send_message(chat_id=chat_id, text=name_success_text.format(name=update.message.text, id=users[-1]['id']))
    else:
        await context.bot.send_message(chat_id=chat_id, text=name_already_exists_text)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.callback_query.answer()

    chat_id = update.effective_chat.id
    logger.info(f"Checking subscription for chat_id: {chat_id}")


    required_channels = [url_subscribe_1.split("t.me/")[-1]]
    #required_channels = [url_subscribe_1.split("t.me/")[-1], url_subscribe_2.split("t.me/")[-1]]

    user_is_subscribed = True

    for channel in required_channels:
        try:
            member = await context.bot.get_chat_member(f"@{channel}", chat_id)
            if member.status not in ["member", "administrator", "creator"]:
                user_is_subscribed = False
                break
        except Exception as e:
            logger.warning(f"Ошибка при проверке подписки на канал @{channel}: {e}")
            user_is_subscribed = False
            break

    if not user_is_subscribed:
        await context.bot.send_message(chat_id=chat_id, text=not_subscribed_text)
        return

    users = get_users_by_chat_id(chat_id)
    if users and users[-1]["status"] == 4:
        await context.bot.send_message(chat_id=chat_id, text=video_link_text.format(video_link=users[-1]["video_link"]), parse_mode="HTML")
        update_user(users[-1]["id"], {"status": 5, "video_link": users[-1]["video_link"], "chat_id": chat_id, "name": users[-1]["name"]})
    else:
        await context.bot.send_message(chat_id=chat_id, text=unknown_command_text)