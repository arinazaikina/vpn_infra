from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")
SSH_KEY_NAME = os.getenv("SSH_KEY_NAME")
SSH_PRIVATE_KEY_PATH = os.getenv("SSH_PRIVATE_KEY_PATH")
SSH_PUBLIC_KEY_PATH = os.getenv("SSH_PUBLIC_KEY_PATH")
USER = os.getenv("USER")
