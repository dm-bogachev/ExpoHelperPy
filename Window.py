import threading
import tkinter as tk
from tkinter import ttk, messagebox
from CyberduckUploader import CyberduckUploader
from Robot import Robot
from TelegramBot import TelegramBot
from UserService import UserService
from Config import Config
from VideoEditor import VideoEditor
from VideoRecorder import VideoRecorder
import logging
import qrcode
import handlers
import asyncio

logging.getLogger("httpcore.http11").setLevel(logging.CRITICAL)
logging.getLogger("httpcore.connection").setLevel(logging.CRITICAL)


class Window(tk.Tk):
    def __init_classes(self):
        Config.init()
        UserService.init()
        self.robot = Robot()
        self.telegrambot = TelegramBot()
        self.recorder = VideoRecorder()
        self.editor = VideoEditor()
        self.s3 = CyberduckUploader()

        # self.telegram_logger = logging.getLogger("telegram")
        # self.telegram_logger.setLevel(logging.CRITICAL)
        # self.telegram_logger.propagate = False
        # for handler in self.telegram_logger.handlers[:]:
        #     self.telegram_logger.removeHandler(handler)

        self.robot.start()
        self.telegrambot.start()

    def __init_ui(self):
        self.title("Великий кинеботер робовизарда v0.0.0.1")
        self.geometry("1200x600")

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        self.update_btn = tk.Button(btn_frame, text="Свет! Камера! Мотор!", command=self.on_start_cinema_click)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        self.__init_tree()
        try:
            self.refresh_icon = tk.PhotoImage(file="refresh.png")
            self.refresh_btn = tk.Button(btn_frame, image=self.refresh_icon, command=self.refresh_data)
        except Exception as e:
            self.refresh_btn = tk.Button(btn_frame, text="Обновить список", command=self.refresh_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
                # Кнопка для отображения QR кода
        self.show_qr_btn = tk.Button(btn_frame, text="Показать QR код", command=self.show_qr_code)
        self.show_qr_btn.pack(side=tk.LEFT, padx=5)
        
        self.copy_link_btn = tk.Button(btn_frame, text="Скопировать публичную ссылку", command=self.copy_public_link)
        self.copy_link_btn.pack(side=tk.LEFT, padx=5)
        # Кнопка для удаления выбранной записи
        self.delete_record_btn = tk.Button(btn_frame, text="Удалить запись", command=self.delete_record)
        self.delete_record_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка для удаления выбранной записи
        self.service_pos = tk.Button(btn_frame, text="Сервисное положение", command=self.service_pos_f)
        self.service_pos.pack(side=tk.LEFT, padx=5)

                # Кнопка для удаления выбранной записи
        self.start_pos = tk.Button(btn_frame, text="Домашнее положение", command=self.home_pos_f)
        self.start_pos.pack(side=tk.LEFT, padx=5)

        self.__init_create_form()

    def __init_tree(self):
        self.tree_columns = ("id", "chat_id", "full_name", "phone_number", "email", "company_name", "position", "video_link")
        self.tree = ttk.Treeview(self, columns=self.tree_columns, show='headings')
        for col in self.tree_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, )
        self.tree.pack(expand=True, fill=tk.BOTH)
        pass

    def __init__(self):
        super().__init__()
        self.__init_ui()
        self.__init_classes()
        self.refresh_allowed = True

        self.check_robot_connection()
        self.refresh_data()

    def copy_public_link(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя из списка")
            return        
        values = self.tree.item(selected[0])["values"]
        public_link = values[7] if len(values) > 7 else ""
        if public_link:
            self.clipboard_clear()
            self.clipboard_append(public_link)
            messagebox.showinfo("Информация", "Публичная ссылка скопирована в буфер обмена")
        else:
            messagebox.showwarning("Внимание", "У выбранного пользователя нет публичной ссылки")

    def check_robot_connection(self):
        if self.refresh_allowed:     
            if self.robot.connection.connected:
                self.update_btn.config(state=tk.NORMAL)
            else:
                self.update_btn.config(state=tk.DISABLED)
        self.after(1000, self.check_robot_connection)

    def refresh_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        users = UserService.get_all_users()
        users = sorted(users, key=lambda u: u.id, reverse=True)

        for u in users:
            self.tree.insert("", "end", values=(
                u.id,
                u.chat_id,
                u.full_name,
                u.phone_number,
                u.email,
                u.company_name,
                u.position,
                u.video_link
            ))

        items = self.tree.get_children()
        if items:
            first_item = items[0]
            self.tree.selection_set(first_item)
            self.tree.focus(first_item)

    def on_start_cinema_click(self):
        self.update_btn.config(state=tk.DISABLED)
        self.refresh_allowed = False
        threading.Thread(target=self.start_cinema, daemon=True).start()

    def service_pos_f(self):
        self.robot.send_service()

    def home_pos_f(self):
        self.robot.send_home()

    def start_cinema(self):

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя для обновления")
            return
        chat_id = self.tree.item(selected[0])["values"][1]
        if chat_id == 0:
            chat_id_str = self.tree.item(self.tree.selection()[0])["values"][2]
            print(self.tree.item(selected[0])["values"][0])
            user = UserService.get_user_by_id(self.tree.item(selected[0])["values"][0])
        else:
            user = UserService.get_user_by_chat_id(chat_id)
            chat_id_str = chat_id
        
        self.recorder.start_recording(f"{chat_id_str}.mp4")
        self.robot.send_start()
        self.robot.wait_response(timeout=360)
        self.recorder.stop_recording()

        self.editor.trim_and_add_audio(f"video/{chat_id_str}.mp4",
                                       Config.get("cut_AB")[0], 
                                       Config.get("cut_AB")[1], 
                                       f"video/{chat_id_str}_g.mp4")

        remote_path = self.s3.upload_file(f"video/{chat_id_str}_g.mp4", f"{chat_id_str}_g.mp4")
        if remote_path:
            public_link = self.s3.generate_public_link(f"{chat_id_str}_g.mp4")
            if (chat_id == 0 or chat_id is None) and user:
                UserService.update_user_by_id(user.id, video_link=public_link)
            else:
                UserService.update_user(chat_id, video_link=public_link)
            print(f"Public link: {public_link}")
        
        future = asyncio.run_coroutine_threadsafe(handlers.ask_to_subscribe(self.telegrambot.app, chat_id),
                                                     self.telegrambot.loop)
        try:
            result = future.result(timeout=5)
        except Exception as e:
            print(f"Ошибка при выполнении ask_to_subscribe: {e}")

        self.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
        self.after(0, self.enable_refresh)

        pass
    def enable_refresh(self):
        self.refresh_allowed = True
        self.refresh_data()

    #         public_link = uploader.generate_public_link(REMOTE_FILE)
    #         print(f"Public link: {public_link}")
    #     import asyncio
    #     # asyncio.run_coroutine_threadsafe(
    #     #    self.bot_thread.send_message(chat_id, f"Ваше видео: {public_link}"),
    #     #    self.bot_thread.loop
    #     # )
    #     # future = asyncio.run_coroutine_threadsafe(handlers.ask_to_subscribe(self.bot_thread.app, chat_id),
    #     #                                              self.bot_thread.loop)
    #     # try:
    #     #     result = future.result(timeout=5)
    #     # except Exception as e:
    #     #     print(f"Ошибка при выполнении ask_to_subscribe: {e}")
    def __init_create_form(self):
        form_frame = tk.Frame(self)
        form_frame.pack(fill=tk.X, padx=5, pady=10)

        header = tk.Label(form_frame, text="Создать новую запись:", font=("Arial", 10, "bold"))
        header.grid(row=0, column=0, columnspan=7, sticky="w", pady=(0, 5))

        # Определяем поля: (метка, имя_атрибута)
        fields = [
            #("Chat ID:", "new_chat_id"),
            ("Имя:", "new_full_name"),
            ("Телефон:", "new_phone_number"),
            ("Email:", "new_email"),
            ("Компания:", "new_company_name"),
            ("Должность:", "new_position"),
            #("Видео ссылка:", "new_video_link")
        ]

        # Располагаем метки в строке 1 и поля ввода в строке 2
        for idx, (label_text, attr_name) in enumerate(fields):
            lbl = tk.Label(form_frame, text=label_text)
            lbl.grid(row=1, column=idx, padx=5, sticky="w")
            entry = tk.Entry(form_frame)
            entry.grid(row=2, column=idx, padx=5, sticky="w")
            setattr(self, attr_name, entry)

        self.create_btn = tk.Button(form_frame, text="Добавить запись", command=self.create_record)
        self.create_btn.grid(row=3, column=0, columnspan=len(fields), pady=10)
    
    def create_record(self):
        # Читаем значения из формы
        #chat_id = self.new_chat_id.get().strip()
        full_name = self.new_full_name.get().strip()
        phone_number = self.new_phone_number.get().strip()
        email = self.new_email.get().strip()
        company_name = self.new_company_name.get().strip()
        position = self.new_position.get().strip()
        #video_link = self.new_video_link.get().strip()

        if  not full_name:
            messagebox.showwarning("Внимание", "Необходимо заполнить обязательные поля: Chat ID и Имя.")
            return

        # Добавляем запись через UserService.add_user.
        # Обратите внимание, что могут потребоваться дополнительные поля.
        try:
            from UserService import UserService  # если импорт уже не выполнен вверху
            UserService.add_user(
                chat_id=0,
                full_name=full_name,
                phone_number=phone_number,
                email=email,
                company_name=company_name,
                position=position,
                video_link="no",
                is_subscribed=False  # можно задать значение по умолчанию
            )
            messagebox.showinfo("Информация", "Запись успешно добавлена.")
            self.refresh_data()  # обновляем таблицу
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {e}")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        confirm = messagebox.askyesno("Подтверждение", "Удалить выбранную запись?")
        if not confirm:
            return
        values = self.tree.item(selected[0])["values"]
        record_id = values[0]  # предполагается, что id находится в первом столбце
        try:
            UserService.delete_user_by_id(record_id)
            messagebox.showinfo("Информация", "Запись удалена")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись: {e}")

    def show_qr_code(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя для отображения QR кода")
            return
        
        values = self.tree.item(selected[0])["values"]
        if len(values) > 7 and values[7]:
            video_link = values[7]
        else:
            messagebox.showwarning("Внимание", "У выбранного пользователя нет video_link")
            return
        
        try:
            
            from PIL import Image, ImageTk
        except ImportError:
            messagebox.showerror("Ошибка", "Не установлены необходимые модули. Установите qrcode и Pillow.")
            return
        
        # Генерация QR кода
        qr = qrcode.make(video_link)
        
        # Создание модального окна для показа QR кода
        qr_window = tk.Toplevel(self)
        qr_window.title("QR код")
        # Преобразование изображения в формат, используемый tkinter
        qr_photo = ImageTk.PhotoImage(qr)
        label = tk.Label(qr_window, image=qr_photo)
        label.image = qr_photo  # предотвращает сборку мусора
        label.pack(padx=10, pady=10)
        close_btn = tk.Button(qr_window, text="Закрыть", command=qr_window.destroy)
        close_btn.pack(pady=5)
        
if __name__ == "__main__":
    app = Window()
    app.mainloop()
