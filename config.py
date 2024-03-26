from aiogram import Bot
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)

REDIS_URL = 'redis://localhost:6379/'
ECHO = True
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')


class Settings(BaseSettings):
    TOKEN: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def database_url_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file=env_path)


settings = Settings()
