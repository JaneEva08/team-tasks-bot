"""Обработчики команд /add, /list и /list_csv."""
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from database import db

router = Router()

# Telegram не принимает сообщения длиннее 4096 символов
TELEGRAM_MESSAGE_LIMIT = 4096
MAX_TASK_LENGTH = 1000


def split_into_messages(blocks: list[str], limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    """Собирает блоки текста в сообщения, каждое не длиннее limit символов.

    Блок не разрывается посередине, если он сам помещается в лимит.
    """
    messages: list[str] = []
    current = ""
    for block in blocks:
        candidate = f"{current}\n{block}" if current else block
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            messages.append(current)
        # Слишком длинный блок режем на куски
        while len(block) > limit:
            messages.append(block[:limit])
            block = block[limit:]
        current = block
    if current:
        messages.append(current)
    return messages


class AddTaskStates(StatesGroup):
    """Состояния диалога добавления задачи (FSM)."""

    waiting_for_text = State()  # бот ждёт, пока пользователь пришлёт текст задачи


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    """Запускает сценарий добавления задачи: просит прислать текст."""
    await message.answer("✏️ Введите текст задачи:")
    await state.set_state(AddTaskStates.waiting_for_text)


@router.message(AddTaskStates.waiting_for_text)
async def process_task_text(message: Message, state: FSMContext) -> None:
    """Сохраняет присланный текст как новую задачу в базе данных."""
    task_text = (message.text or "").strip()

    # Фото, стикер или пустое сообщение раньше роняли запись в базу
    # (поле text NOT NULL) — теперь просим прислать текст ещё раз.
    if not task_text:
        await message.answer("⚠️ Пришлите задачу текстом, например: «Подготовить отчёт к пятнице».")
        return
    if len(task_text) > MAX_TASK_LENGTH:
        await message.answer(
            f"⚠️ Слишком длинная задача: {len(task_text)} символов, максимум {MAX_TASK_LENGTH}. "
            "Сократите текст и пришлите ещё раз."
        )
        return

    author = message.from_user.username or message.from_user.full_name

    task_id = db.add_task(text=task_text, user=author)

    await message.answer(
        f"✅ Задача успешно добавлена!\n\n"
        f"🆔 ID: {task_id}\n"
        f"📝 Текст: {task_text}\n"
        f"👤 Автор: {author}"
    )
    await state.clear()  # сбрасываем состояние — диалог добавления завершён


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    """Выводит список всех сохранённых задач."""
    tasks = db.get_all_tasks()

    if not tasks:
        await message.answer("📭 Список задач пуст. Добавьте первую задачу с помощью /add")
        return

    # Показываем последние добавленные задачи сверху
    blocks = ["📋 Список всех задач:\n"]
    for task_id, text, user, created_at in reversed(tasks):
        blocks.append(
            f"🔹 ID: {task_id}\n📝 {text}\n👤 {user}\n🕒 {created_at}\n"
        )

    # Длинный список отправляем несколькими сообщениями
    for chunk in split_into_messages(blocks):
        await message.answer(chunk)


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message) -> None:
    """Выгружает все задачи в CSV-файл и отправляет его пользователю."""
    tasks = db.get_all_tasks()

    if not tasks:
        await message.answer("📭 Список задач пуст, экспортировать нечего.")
        return

    file_path = db.export_to_csv()
    try:
        csv_file = FSInputFile(file_path)
        await message.answer_document(
            csv_file, caption=f"📊 Список задач ({len(tasks)} шт.)"
        )
    finally:
        os.remove(file_path)  # временный файл больше не нужен после отправки
