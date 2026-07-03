# Конфигурация проекта: загружаем переменные окружения из файла .env
import os
from dotenv import load_dotenv

load_dotenv()  # читает файл .env и подгружает переменные в окружение процесса

BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен бота, выданный @BotFather

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден. Создай файл .env на основе .env.example и вставь туда токен бота."
    )
