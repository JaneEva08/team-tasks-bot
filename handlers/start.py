"""Обработчик команды /start."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Приветствует пользователя и рассказывает про доступные команды."""
    await message.answer(
        "👋 Привет! Я бот для командной работы с задачами.\n\n"
        "📋 Доступные команды:\n"
        "/start — показать это сообщение\n"
        "/add — добавить новую задачу\n"
        "/list — показать все задачи\n"
        "/list_csv — скачать список задач в формате CSV\n\n"
        "💡 Используй /add, чтобы добавить задачу в общий список!"
    )
