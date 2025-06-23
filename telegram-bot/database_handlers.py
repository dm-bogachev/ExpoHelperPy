import requests
from Config import Config

BASE_URL = Config.get("database_api_url", "http://localhost:8000/api/database") 

def get_all_users():
    try:
        response = requests.get(f"{BASE_URL}/users")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_user(user_id: int):
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_users_by_chat_id(chat_id: int):
    try:
        response = requests.get(f"{BASE_URL}/users/by_chat/{chat_id}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

def get_users_by_status(status: int):
    try:
        response = requests.get(f"{BASE_URL}/users/by_status/{status}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

def add_user(user_data: dict):
    try:
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def update_user(user_id: int, user_data: dict):
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=user_data)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def delete_user(user_id: int):
    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False
