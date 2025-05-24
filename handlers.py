import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from BitrixService import BitrixService
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
        await context.bot.send_message(chat_id, "Вопрос 2: Введите ваш номер телефона (в формате +7XXXXXXXXXX):")
    elif state.questionnaire_status == 2:
        state.phone_number = text
        state.questionnaire_status += 1
        await context.bot.send_message(chat_id, "Вопрос 3: Введите адрес вашей электронной почты:")
    elif state.questionnaire_status == 3:
        state.email = text
        state.questionnaire_status += 1
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Пропуск", callback_data="skip_company")]])
        await context.bot.send_message(
            chat_id,
            "Вопрос 4: Введите название вашей компании или нажмите кнопку «Пропуск»:",
            reply_markup=keyboard
        )
    elif state.questionnaire_status == 4:
        if text.lower() != "пропуск":
            state.company_name = text
        state.questionnaire_status += 1
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Пропуск", callback_data="skip_position")]])
        await context.bot.send_message(
            chat_id,
            "Вопрос 5: Введите вашу должность или нажмите кнопку «Пропуск»:",
            reply_markup=keyboard
        )
    elif state.questionnaire_status == 5:
        if text.lower() != "пропуск":
            state.position = text
        state.questionnaire_status = 0
        await commands.ask_interest_command(update, context)
        #await context.bot.send_message(chat_id, "Спасибо за информацию!", reply_markup=ReplyKeyboardRemove())

        # Проверяем, существует ли пользователь
        # existing_user = UserService.get_user_by_chat_id(chat_id)
        # if existing_user:
        #     UserService.update_user_from_userdata(state)
        # else:
        #     UserService.add_user_from_userdata(state)
        #await ask_for_waiting(context, chat_id)

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
        [InlineKeyboardButton("Подписаться на канал", url="https://t.me/robotics_expert")],
        [InlineKeyboardButton("Я подписался / Уже подписан", callback_data="subscribed")]
    ])
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_data = update.callback_query.data
    chat_id = update.callback_query.message.chat_id

    await update.callback_query.answer()

    if query_data == "start_kinebot_questions":
        user_states[chat_id] = UserData(chat_id=chat_id, questionnaire_status=1)
        await context.bot.send_message(chat_id, "Вопрос 1: Как вас зовут? Введите ваше полное имя:")
    elif query_data == "skip_company":
        state = user_states.get(chat_id)
        if state:
            state.questionnaire_status += 1
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Пропуск", callback_data="skip_position")]])
            await context.bot.send_message(
                chat_id,
                "Вопрос 5: Введите вашу должность или нажмите кнопку «Пропуск»:",
                reply_markup=keyboard
            )
    elif query_data == "skip_position":
        state = user_states.get(chat_id)
        if state:
            state.questionnaire_status = 0
            logging.info(f"Получены данные пользователя: {state}")
            await commands.ask_interest_command(update, context)
    elif query_data == "subscribed":
        # Проверяем, подписан ли пользователь на канал
        is_subscribed = await is_user_subscribed(context, chat_id, "@robotics_expert")
        if not is_subscribed:
            await context.bot.send_message(chat_id, "Пожалуйста, подпишитесь на канал и нажмите кнопку снова.")
            return
        user = UserService.get_user_by_chat_id(chat_id)
        link = user.video_link
        await context.bot.send_message(chat_id, f"Спасибо за подписку! Вот ваше видео: {link}\n" +
                                       "Ссылка будет действительна в течение недели.")
    elif query_data.startswith("interest_"):
        state = user_states.get(chat_id)
        state.user_interest = query_data
        logging.info(f"Получены данные пользователя: {state}")
        # Проверяем, существует ли пользователь
        existing_user = UserService.get_user_by_chat_id(chat_id)
        if existing_user:
            UserService.update_user_from_userdata(state)
        else:
            UserService.add_user_from_userdata(state)
        if query_data in ["interest_active", "interest_considering"]:
            success = BitrixService.send_lead_to_bitrix(state)
            logging.info("Успешно отправлено" if success else "Ошибка при отправке")

        await context.bot.send_message(chat_id, "Спасибо за участие в опросе! Теперь подойдите к оператору кинебота для съёмки видео!")

async def is_user_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int, channel_username: str) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        from telegram.constants import ChatMemberStatus
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER, ChatMemberStatus.LEFT]
    except Exception as e:
        logging.warning(f"Ошибка при проверке подписки: {e}")
        return False

async def final_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    text = (
        "🤖 Рады, что вы познакомились с нашим Кинеботом на стенде А42!\n"
        " - Поговорите с инженерами Robowizard\n"
        " - Увидьте live-демонстрацию роботов\n"
        " - Обсудите индивидуальные решения\n\n"
        "Ждём вас до конца выставки!"
    )
    await context.bot.send_message(chat_id, text)