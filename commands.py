import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text if update.message.text else ""
    args = message.split()
    parameter = args[1] if len(args) > 1 else ""
    if parameter == "kinebotvideo":
        await video_command(update, context)
    elif parameter == "posmaterials":
        await pos_materials_command(update, context)
    else:
        await video_command(update, context)
        #await default_options_command(update, context)

async def default_options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = "Добро пожаловать в Robowizard! Выберите один из вариантов ниже:"
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("Хочу видео"), KeyboardButton("POS Материалы")]],
        resize_keyboard=True
    )
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Возможен вызов как из команды, так и через callback
    chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    text = (
        "👋 Это команда Robowizard - специалисты в промышленной роботизации уже более 15 лет! "
        "Мы помогаем предприятиям пройти путь от аудита до внедрения.\n\n"
        "Спасибо за использование \"Кинебота\" на выставке \"Металлообработка 2025\"!\n\n"
        "Чтобы получить уникальное видео 360°, нужно ответить на 6 вопросов.\n\n"
        "Готовы продолжить? 👇"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Да, хочу получить видео", callback_data="start_kinebot_questions")]
    ])
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

async def pos_materials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = "Спасибо за интерес к нашим материалам! Следуйте инструкции для получения POS-материалов."
    await context.bot.send_message(chat_id, text)

async def ask_interest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Возможен вызов как из команды, так и через callback
    chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    text = (
        "Вопрос 6: Насколько вы или ваша компания заинтересована в решениях по промышленной роботизации в ближайшие 1-2 года?"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Активно ищем решения", callback_data="interest_active")],
        [InlineKeyboardButton("Интересно, рассматриваем возможности", callback_data="interest_considering")],
        [InlineKeyboardButton("Пока не планируем, но интересно узнать", callback_data="interest_not_now")],
        [InlineKeyboardButton("Не интересует", callback_data="interest_no")]
    ])
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)
