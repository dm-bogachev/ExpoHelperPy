import time
import tkinter as tk
from tkinter import ttk, messagebox
from CyberduckUploader import CyberduckUploader
from Robot import Robot
from TelegramBot import TelegramBot
from UserService import UserService
from Config import Config
from VideoEditor import VideoEditor
from VideoRecorder import VideoRecorder
import os
import commands
import handlers
class UserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("User Data Viewer")
        self.geometry("900x400")

        # Таблица
        columns = ("chat_id", "full_name", "phone_number", "email", "company_name", "position", "is_subscribed")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Кнопка обновления выбранного пользователя
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        self.update_btn = tk.Button(btn_frame, text="Обновить выбранного", command=self.update_selected_user)
        self.update_btn.pack(pady=5)

        Config.load()  # загрузка конфигурации
        UserService.init()  # инициализация базы

        TOKEN = Config.get("telegram_bot_api_token")  # замените на реальный токен
        self.bot_thread = TelegramBot(token=TOKEN)
        self.bot_thread.start()
        # Основной поток может выполнять другие задачи, либо ждать завершения бота:
        #self.bot_thread.join()
        self.refresh_data()
        self.after(10000, self.periodic_refresh)  # обновлять каждые 10 сек

    def refresh_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        users = UserService.get_all_users()
        for u in users:
            self.tree.insert("", "end", values=(
                u.chat_id,
                u.full_name,
                u.phone_number,
                u.email,
                u.company_name,
                u.position,
                u.is_subscribed
            ))

    def periodic_refresh(self):
        self.refresh_data()
        self.after(10000, self.periodic_refresh)

    def update_selected_user(self):

        robot = Robot()
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя для обновления")
            return

        chat_id = self.tree.item(selected[0])["values"][0]
        processor = VideoRecorder()
    
        # Пример запуска записи видео
        processor.start_recording(f"{chat_id}.mp4")
        time.sleep(15)  
        processor.stop_recording()
        editor = VideoEditor(f"video/{chat_id}.mp4")
        editor.trim_and_add_audio(0, 20, f"video/{chat_id}_g.mp4")
        LOCAL_FILE = f"video/{chat_id}_g.mp4"
        REMOTE_FILE = f"{chat_id}_g.mp4"
        
        uploader = CyberduckUploader()
        remote_path = uploader.upload_file(LOCAL_FILE, REMOTE_FILE)
        if remote_path:
            public_link = uploader.generate_public_link(REMOTE_FILE)
            print(f"Public link: {public_link}")
        import asyncio
        #asyncio.run_coroutine_threadsafe(
        #    self.bot_thread.send_message(chat_id, f"Ваше видео: {public_link}"),
        #    self.bot_thread.loop
        #)
        # Запускаем ask_to_subscribe в event loop потока TelegramBot
        #future = asyncio.run_coroutine_threadsafe(handlers.ask_to_subscribe(self.bot_thread.app, chat_id),
        #                                              self.bot_thread.loop)
        # При необходимости можно дождаться результата:
        # try:
        #     result = future.result(timeout=5)  # ждем завершения до 5 секунд
        # except Exception as e:
        #     print(f"Ошибка при выполнении ask_to_subscribe: {e}")

if __name__ == "__main__":
    app = UserApp()
    app.mainloop()
