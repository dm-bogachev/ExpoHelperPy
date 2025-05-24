import json
import os

class Config:
    _config_file = "config.json"
    _default_config = {
        "database_name": "expo_helper.db",
        "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "bitrix_api_url": "YOUR_BITRIX_API_URL",
        "bitrix_allow_send": False,
        "host": "0.0.0.0",              
        "port": 48569,
        "timeout": 5,
        "max_tcp_attempts": 5,
        "ping_interval": 15,
        "connection_timeout": 10, 
        "max_connection_attempts": 3,
        "camera_path": 0,
        "camera_fps": 60,
        "camera_resolution": (2560, 1440),
        "video_folder": "video",
        "cut_AB": (0, 10),
        "sound_name": "sound.mp3",
        "duck_access_key": "YourDuckAccessKey",
        "duck_secret_access_key": "YourDuckSecretAccessKey",
        "duck_bucket_name": "YourDuckBucketName",
        "duck_storage_url": "https://your-duck-storage-url.com",
        "duck_profile": "default",
        "telegram_bot_api_token": "YOUR_TELEGRAM_BOT_API_TOKEN",
        
    }
    _config = {}

    @classmethod
    def load(cls):
        """Загружает конфигурацию из файла или создает с дефолтными значениями."""
        if not os.path.exists(cls._config_file):
            cls._config = cls._default_config.copy()
            cls.save()
        else:
            with open(cls._config_file, "r", encoding="utf-8") as f:
                cls._config = json.load(f)

    @classmethod
    def save(cls):
        """Сохраняет текущую конфигурацию в файл."""
        with open(cls._config_file, "w", encoding="utf-8") as f:
            json.dump(cls._config, f, indent=4, ensure_ascii=False)

    @classmethod
    def get(cls, key, default=None):
        """Получает значение по ключу или дефолт, если ключа нет."""
        return cls._config.get(key, default)

    @classmethod
    def set(cls, key, value):
        """Устанавливает значение по ключу и сохраняет файл."""
        cls._config[key] = value
        cls.save()

if __name__ == "__main__":
    # Пример использования
    Config.load()

   