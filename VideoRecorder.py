import cv2
import threading
import time
import logging
from Config import Config
from UserService import UserService
import os

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class VideoRecorder:
    def __init__(self):
        Config.init()
        UserService.init()

        self.video_source = Config.get('camera_path')
        self.fps = Config.get('camera_fps')
        self.resolution = Config.get('camera_resolution')
        self.video_folder = Config.get('video_folder')

        if not os.path.exists(self.video_folder):
            os.makedirs(self.video_folder)

        self.recording = False
        self.thread = None
        self.camera_ready = threading.Event()  # Новое событие для синхронизации
    
    def start_recording(self, filename):
        self.filename = filename
        if not self.recording:
            self.recording = True
            self.camera_ready.clear()  # Сброс события перед запуском потока
            self.thread = threading.Thread(target=self._record_video)
            self.thread.start()
            
            # Ждем, пока камера не будет проинициализирована (успешно или с ошибкой)
            self.camera_ready.wait()  
            
            logger.info("Video recording started.")
        else:
            logger.warning("Video recording is already in progress.")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.thread.join()
            logger.info("Video recording stopped.")
        else:
            logger.warning("No video recording in progress to stop.")

    def _record_video(self):
        cap = cv2.VideoCapture(self.video_source)
        if not cap.isOpened():
            logger.error("Failed to open video source.")
            self.camera_ready.set()  # Завершаем ожидание в start_recording
            return

        cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0]) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        logger.info(f"Video source opened: {self.video_source}, FPS: {self.fps}, Resolution: {self.resolution}")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(os.path.join(self.video_folder, self.filename), fourcc, self.fps, self.resolution)
        if not out.isOpened():
            logger.error("Failed to open video writer.")
            cap.release()
            self.camera_ready.set()  # Завершаем ожидание в start_recording
            return

        self.camera_ready.set()  # Камера успешно проинициализирована
        frame_period = 1.0 / self.fps

        while self.recording:
            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame from video source.")
                break

            out.write(frame)

            elapsed = time.time() - start_time
            delay = frame_period - elapsed
            if delay > 0:
                time.sleep(delay)

        cap.release()
        out.release()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    processor = VideoRecorder()
    
    # Пример запуска записи видео
    processor.start_recording("output.mp4")
    time.sleep(20)  
    processor.stop_recording()
