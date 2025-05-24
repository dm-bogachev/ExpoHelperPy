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
        self.robot_handler = Robot()
        self.robot_handler.start()
        
        # Таблица
        columns = ("chat_id", "full_name", "phone_number", "email", "company_name", "position", "is_subscribed")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        self.update_btn = tk.Button(btn_frame, text="Обновить выбранного", command=self.update_selected_user)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        try:
            self.refresh_icon = tk.PhotoImage(file="refresh.png")
            self.refresh_btn = tk.Button(btn_frame, image=self.refresh_icon, command=self.refresh_data)
        except Exception as e:
            self.refresh_btn = tk.Button(btn_frame, text="Обновить список", command=self.refresh_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        self.check_robot_connection()
        Config.init() 
        UserService.init() 

        self.bot_thread = TelegramBot()
        #self.bot_thread.start()
        # Основной поток может выполнять другие задачи, либо ждать завершения бота:
        #self.bot_thread.join()
        self.refresh_data()

    # Удалён метод periodic_refresh

    def check_robot_connection(self):
        if self.robot_handler.connection.connected:
            self.update_btn.config(state=tk.NORMAL)
        else:
            self.update_btn.config(state=tk.DISABLED)
        self.after(1000, self.check_robot_connection)

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

    def update_selected_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя для обновления")
            return

        chat_id = self.tree.item(selected[0])["values"][0]
        processor = VideoRecorder()

        # Пример запуска записи видео
        processor.start_recording(f"{chat_id}.mp4")
        self.robot_handler.send_start()
        self.robot_handler.wait_response(timeout=200)
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
        # asyncio.run_coroutine_threadsafe(
        #    self.bot_thread.send_message(chat_id, f"Ваше видео: {public_link}"),
        #    self.bot_thread.loop
        # )
        # future = asyncio.run_coroutine_threadsafe(handlers.ask_to_subscribe(self.bot_thread.app, chat_id),
        #                                              self.bot_thread.loop)
        # try:
        #     result = future.result(timeout=5)
        # except Exception as e:
        #     print(f"Ошибка при выполнении ask_to_subscribe: {e}")

if __name__ == "__main__":
    app = UserApp()
    app.mainloop()
