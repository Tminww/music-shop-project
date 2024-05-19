from dotenv import load_dotenv
import os

load_dotenv()  # loads the configs from .env


class Settings:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    API_KEY_YOOKASSA = os.getenv("API_KEY_YOOKASSA")
    ID_SHOP_YOOKASSA = os.getenv("ID_SHOP_YOOKASSA")


settings = Settings()
