import requests
from Config import Config

import logging
logger = logging.getLogger("database_handlers")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

BASE_URL = Config.get("database_api_url", "http://localhost:8000/api/database") 

def get_all_users():
    try:
        logger.debug("Fetching all users from the database API")
        response = requests.get(f"{BASE_URL}/users")
        response.raise_for_status()
        logger.debug("Successfully fetched all users")
        return response.json()
    except requests.RequestException:
        logger.error("Error fetching all users")
        return None

def get_user(user_id: int):
    try:
        logger.debug(f"Fetching user {user_id} from the database API")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        logger.debug(f"Successfully fetched user {user_id}")
        return response.json()
    except requests.RequestException:
        logger.error(f"Error fetching user {user_id}")
        return None

def get_users_by_chat_id(chat_id: int):
    try:
        logger.debug(f"Fetching users by chat_id {chat_id} from the database API")
        response = requests.get(f"{BASE_URL}/users/by_chat/{chat_id}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        logger.debug(f"Successfully fetched users by chat_id {chat_id}")
        return response.json()
    except requests.RequestException:
        logger.error(f"Error fetching users by chat_id {chat_id}")
        return []

def get_users_by_status(status: int):
    try:
        logger.debug(f"Fetching users by status {status} from the database API")
        response = requests.get(f"{BASE_URL}/users/by_status/{status}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        logger.debug(f"Successfully fetched users by status {status}")
        return response.json()
    except requests.RequestException:
        logger.error(f"Error fetching users by status {status}")
        return []

def add_user(user_data: dict):
    try:
        logger.debug("Adding user to the database API with data: %s", user_data)
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        response.raise_for_status()
        logger.debug("Successfully added user")
        return response.json()
    except requests.RequestException:
        logger.error("Error adding user")
        return None

def update_user(user_id: int, user_data: dict):
    try:
        logger.debug(f"Updating user {user_id} in the database API with data: %s", user_data)
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=user_data)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        logger.debug(f"Successfully updated user {user_id}")
        return response.json()
    except requests.RequestException:
        logger.error(f"Error updating user {user_id}")
        return None

def delete_user(user_id: int):
    try:
        logger.debug(f"Deleting user {user_id} from the database API")
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 404:
            return False
        response.raise_for_status()
        logger.debug(f"Successfully deleted user {user_id}")
        return True
    except requests.RequestException:
        logger.error(f"Error deleting user {user_id}")
        return False
