import json
import os

if os.environ.get("DOCKER"):
    config_path = "/shared_data/configs/robot.json"
else:
    config_path = os.path.join(os.path.dirname(__file__), 'local', "robot.json")
os.makedirs(os.path.dirname(config_path), exist_ok=True)

class Config:
    _config_file = config_path
    _default_config = {
        "debug_level": "INFO",
    }
    _config = {}


    @classmethod
    def init(cls):
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

Config.init()
   