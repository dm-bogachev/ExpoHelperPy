import requests
from Config import *

class BitrixService:

    @classmethod
    def send_lead_to_bitrix(cls, user):

        Config.load()
        bitrix_api_url = Config.get("bitrix_api_url")
        bitrix_allow_send = Config.get("bitrix_allow_send")

        if not bitrix_allow_send:
            print("Отправка в Битрикс отключена")
            return False

        lead = {
            "fields": {
                "TITLE": f"Металлообработка лид с кинебота {user.full_name}",
                "NAME": user.full_name,
                "SECOND_NAME": user.full_name,
                "LAST_NAME": user.full_name,
                "STATUS_ID": "NEW",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "CURRENCY_ID": "RUR",
                "PHONE": [{"VALUE": user.phone_number, "VALUE_TYPE": "WORK"}],
                "WEB": [{"VALUE": user.email, "VALUE_TYPE": "WORK"}],
                "COMPANY_TITLE": user.company_name,
                "POST": user.position,
                "COMMENTS": user.user_interest,
            },
            "params": {
                "REGISTER_SONET_EVENT": "Y"
            }
        }

        response = requests.post(bitrix_api_url, json=lead)
        return response.ok

if __name__ == "__main__":
    # Example usage

    from UserService import *
    Config.load()
    UserService.init()
    user = UserService.get_user_by_chat_id(987654321)

    if user:
        success = BitrixService.send_lead_to_bitrix(user)
        print("Успешно отправлено" if success else "Ошибка при отправке")