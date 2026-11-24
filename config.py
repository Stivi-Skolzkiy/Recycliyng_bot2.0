
import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Загружаем настройки из файла .env
load_dotenv()


@dataclass
class Settings:
    # Токен Telegram-бота.
    # Пока оставляем пустым: добавим после создания бота через BotFather.
    bot_token: str

    # Параметры подключения к PostgreSQL
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str


def load_settings() -> Settings:
    """Считывает настройки проекта из файла .env."""

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", ""),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", ""),
    )


settings = load_settings()


# Проверяем, что основные параметры базы данных заполнены
if not settings.db_name:
    raise ValueError("Не указано название базы данных в файле .env")

if not settings.db_password:
    raise ValueError("Не указан пароль PostgreSQL в файле .env")
