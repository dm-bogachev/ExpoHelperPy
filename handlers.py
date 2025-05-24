import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from UserData import UserData
from UserService import UserService
import commands

# Глобальное хранилище состояний пользователей
user_states = {}

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in user_states and user_states[chat_id].questionnaire_status > 0:
        await handle_user_input(update, context)
        return
    if "Хочу видео" in update.message.text:
        await commands.video_command(update, context)
        return
    await update.message.reply_text("Неизвестная команда. Попробуйте /start")
    

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    state = user_states.get(chat_id)
    if not state:
        return

    if state.questionnaire_status == 1:
        state.full_name = text
        state.questionnaire_status += 1
        await context.bot.send_message(chat_id, "Спасибо! Теперь, пожалуйста, поделитесь контактом (номер телефона).")
    elif state.questionnaire_status == 2:
        state.phone_number = text
        state.questionnaire_status += 1
        await context.bot.send_message(chat_id, "Отлично! Введите вашу электронную почту.")
    elif state.questionnaire_status == 3:
        state.email = text
        state.questionnaire_status += 1
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("Пропуск")]], resize_keyboard=True)
        await context.bot.send_message(chat_id, "Укажите, пожалуйста, название вашей компании.", reply_markup=keyboard)
    elif state.questionnaire_status == 4:
        if text.lower() != "пропуск":
            state.company_name = text
        state.questionnaire_status += 1
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("Пропуск")]], resize_keyboard=True)
        await context.bot.send_message(chat_id, "Какую должность вы занимаете?", reply_markup=keyboard)
    elif state.questionnaire_status == 5:
        if text.lower() != "пропуск":
            state.position = text
        state.questionnaire_status = 0
        await context.bot.send_message(chat_id, "Спасибо за информацию!", reply_markup=ReplyKeyboardRemove())

        logging.info(f"Получены данные пользователя: {state}")
        UserService.add_user_from_userdata(state)
        await ask_for_waiting(context, chat_id)

async def ask_for_waiting(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    text = (
        "Теперь подойдите к оператору кинебота для съёмки видео!.\n"
    )
    await context.bot.send_message(chat_id, text)

async def ask_to_subscribe(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    text = (
        "Чтобы получить доступ к видео, подпишитесь на наш Telegram-канал:\n"
        "• Новости роботизации\n"
        "• Кейсы внедрения\n"
        "• Полезные материалы\n\n"
        "👇 Нажмите на кнопку ниже, подпишитесь и вернитесь в чат."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Подписаться на канал", url="https://t.me/kawasakiroboticsrus")],
        [InlineKeyboardButton("Я подписался", callback_data="subscribed")]
    ])
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_data = update.callback_query.data
    chat_id = update.callback_query.message.chat_id

    await update.callback_query.answer()

    if query_data == "start_kinebot_questions":
        # Инициализируем или сбрасываем состояние диалога
        user_states[chat_id] = UserData(chat_id=chat_id, questionnaire_status=1)
        await context.bot.send_message(chat_id, "Для продолжения введите ФИО:")
    elif query_data == "subscribed":
        # Считаем, что пользователь подписался; в реальном проекте следует проверить подписку
        await context.bot.send_message(chat_id, "Спасибо за подписку! Продолжаем...")
        await commands.ask_interest_command(update, context)
    elif query_data.startswith("interest_"):
        if query_data in ["interest_active", "interest_considering"]:
            response = (
                "Отлично! Вот ваше видео 360° с выставки \"Металлообработка 2025\"!\n\n"
                "Наша технология позволяет создавать эффектный контент. Посетите наш стенд (А42) или свяжитесь с нами."
            )
        else:
            response = (
                "Вот ваше видео 360° с выставки \"Металлообработка 2025\"!\n\n"
                "Благодарим за участие. Если у вас возникнет интерес к роботизации, обращайтесь к нам."
            )
        await context.bot.send_message(chat_id, response)
        video_path = "Videos/user_253712517.mp4"
        await commands.send_video(update, context, video_path)
        await final_message(context, chat_id)

async def final_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    text = (
        "🤖 Рады, что вы познакомились с нашим Кинеботом на стенде А42!\n"
        " - Поговорите с инженерами Robowizard\n"
        " - Увидьте live-демонстрацию роботов\n"
        " - Обсудите индивидуальные решения\n\n"
        "Ждём вас до конца выставки!"
    )
    await context.bot.send_message(chat_id, text)