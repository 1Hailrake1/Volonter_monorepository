import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    FAST_API_DATABASE_URI = os.getenv("DATABASE_URL_ASYNC")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW"))
    LOG_DIR = os.getenv("LOG_DIR")
    DEFAULT_DIR = os.getenv("DEFAULT_DIR")
    DEFAULT_PRIV = os.getenv("DEFAULT_PRIV")
    DEFAULT_PUB = os.getenv("DEFAULT_PUB")
    KEY_SIZE = int(os.getenv("KEY_SIZE"))
    ACCESS_TOKEN_NAME = os.getenv("ACCESS_TOKEN_NAME")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE"))
    JWT_PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH")
    JWT_PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH")
    JWT_KEY_ID = os.getenv("JWT_KEY_ID")
    VERIFY_CODE_EXPIRE = int(os.getenv("VERIFY_CODE_EXPIRE"))
    VERIFY_TOKEN_EXPIRE = int(os.getenv("VERIFY_TOKEN_EXPIRE"))
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM")
    VERIFY_TOKEN_NAME = os.getenv("VERIFY_TOKEN_NAME")

settings = Settings()