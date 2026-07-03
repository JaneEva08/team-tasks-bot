"""Обработчики команд /add, /list и /list_csv."""
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from database import db

router = Router()


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
    task_text = message.text
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
    lines = ["📋 Список всех задач:\n"]
    for task_id, text, user, created_at in reversed(tasks):
        lines.append(
            f"🔹 ID: {task_id}\n📝 {text}\n👤 {user}\n🕒 {created_at}\n"
        )

    await message.answer("\n".join(lines))


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
