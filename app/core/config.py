import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

class Config(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL') or ""
    TEST_DATABASE_URL: str = os.getenv('TEST_DATABASE_URL') or ""
    REDIS_URL: str = os.getenv('REDIS_URL') or ""
    TEST_REDIS_URL: str = os.getenv('TEST_REDIS_URL') or ""
    SECRET_KEY: str = os.getenv('SECRET_KEY') or ""
    ALGORITHM: str = os.getenv('ALGORITHM') or ""
    EXPIRE_MINUTES: str = os.getenv('EXPIRE_MINUTES') or ""
    BCRYPT_SALT_ROUNDS: str = os.getenv('BCRYPT_SALT_ROUNDS') or ""

    model_config = SettingsConfigDict()

config = Config()
