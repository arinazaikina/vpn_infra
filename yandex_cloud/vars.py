import os

from dotenv import load_dotenv

load_dotenv()
USER = os.getenv("USER")
AUTHORIZED_KEY_PATH = os.getenv("AUTHORIZED_KEY_PATH")
FOLDER_ID = os.getenv("FOLDER_ID")
SSH_KEY_NAME = os.getenv("SSH_KEY_NAME")
SSH_PRIVATE_KEY_PATH = os.getenv("SSH_PRIVATE_KEY_PATH")
SSH_PUBLIC_KEY_PATH = os.getenv("SSH_PUBLIC_KEY_PATH")
YANDEX_EMAIL = os.getenv("YANDEX_EMAIL")
YANDEX_EMAIL_PASSWORD = os.getenv("YANDEX_EMAIL_PASSWORD")
