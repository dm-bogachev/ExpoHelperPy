import requests
import logging
from Config import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class BitrixService:

    @classmethod
    def send_lead_to_bitrix(cls, user):
        Config.init()
        bitrix_api_url = Config.get("bitrix_api_url")
        bitrix_allow_send = Config.get("bitrix_allow_send")

        if not bitrix_allow_send:
            logging.info("Отправка в Битрикс отключена")
            return False

        lead = {
            "fields": {
                "TITLE": f"{user.full_name} {user.company_name} (Лид с кинебота)",
                "NAME": user.full_name,
                "SECOND_NAME": "",
                "LAST_NAME": "",
                "STATUS_ID": "UC_9UKVSG",
                "SOURCE_ID": "4",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1691,
                "CURRENCY_ID": "RUR",
                "PHONE": [
                    {"VALUE": user.phone_number, "VALUE_TYPE": "WORK"}
                ],
                "EMAIL": [
                    {"VALUE": user.email, "VALUE_TYPE": "WORK"}
                ],
            },
            "params": {
                "REGISTER_SONET_EVENT": "Y"
            }
        }

        logging.info("Отправка лида в Битрикс: %s", lead)
        response = requests.post(bitrix_api_url, json=lead)
        if response.ok:
            logging.info("Лид успешно отправлен в Битрикс")
        else:
            logging.error("Ошибка при отправке лида в Битрикс: %s %s", response.status_code, response.text)
        return response.ok

if __name__ == "__main__":
    # Example usage
    from UserService import *
    Config.init()
    UserService.init()
    user = UserService.get_user_by_chat_id(987654321)

    if user:
        success = BitrixService.send_lead_to_bitrix(user)
        logging.info("Успешно отправлено" if success else "Ошибка при отправке")