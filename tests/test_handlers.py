"""Тесты обработчиков команд без обращения к Telegram."""
import pytest

from handlers import start, tasks
from handlers.tasks import (
    MAX_TASK_LENGTH,
    TELEGRAM_MESSAGE_LIMIT,
    split_into_messages,
)


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, database):
    """Обработчики работают с чистой базой теста."""
    monkeypatch.setattr(tasks, "db", database)
    return database


async def test_start_lists_all_commands(make_message):
    message = make_message("/start")
    await start.cmd_start(message)
    reply = message.answer.call_args.args[0]
    for command in ("/add", "/list", "/list_csv"):
        assert command in reply


async def test_add_asks_for_text_and_sets_state(make_message, state):
    message = make_message("/add")
    await tasks.cmd_add(message, state)
    message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(tasks.AddTaskStates.waiting_for_text)


async def test_task_text_is_saved(make_message, state, isolated_db):
    message = make_message("  Купить бумагу для принтера  ")
    await tasks.process_task_text(message, state)
    saved = isolated_db.get_all_tasks()
    assert saved[0][1] == "Купить бумагу для принтера"
    assert saved[0][2] == "anna"
    state.clear.assert_awaited_once()


async def test_author_falls_back_to_full_name(make_message, state, isolated_db):
    message = make_message("Задача", username=None)
    await tasks.process_task_text(message, state)
    assert isolated_db.get_all_tasks()[0][2] == "Анна Тестова"


@pytest.mark.parametrize("text", [None, "", "   \n  "])
async def test_non_text_message_does_not_crash(make_message, state, isolated_db, text):
    # Раньше фото или стикер (text=None) роняли обработчик ошибкой БД
    message = make_message(text)
    await tasks.process_task_text(message, state)
    assert isolated_db.get_all_tasks() == []
    state.clear.assert_not_awaited()  # ждём текст дальше
    assert "текстом" in message.answer.call_args.args[0]


async def test_too_long_task_is_rejected(make_message, state, isolated_db):
    message = make_message("а" * (MAX_TASK_LENGTH + 1))
    await tasks.process_task_text(message, state)
    assert isolated_db.get_all_tasks() == []
    assert "Слишком длинная" in message.answer.call_args.args[0]


async def test_task_of_max_length_is_accepted(make_message, state, isolated_db):
    message = make_message("а" * MAX_TASK_LENGTH)
    await tasks.process_task_text(message, state)
    assert len(isolated_db.get_all_tasks()) == 1


async def test_list_empty(make_message):
    message = make_message("/list")
    await tasks.cmd_list(message)
    assert "пуст" in message.answer.call_args.args[0]


async def test_list_shows_newest_first(make_message, isolated_db):
    isolated_db.add_task("Старая", "anna")
    isolated_db.add_task("Новая", "anna")
    message = make_message("/list")
    await tasks.cmd_list(message)
    reply = message.answer.call_args.args[0]
    assert reply.index("Новая") < reply.index("Старая")


async def test_long_list_is_split_into_several_messages(make_message, isolated_db):
    for i in range(30):
        isolated_db.add_task(f"Задача {i} " + "x" * (MAX_TASK_LENGTH - 20), "anna")
    message = make_message("/list")
    await tasks.cmd_list(message)
    replies = [call.args[0] for call in message.answer.call_args_list]
    assert len(replies) > 1
    assert all(len(r) <= TELEGRAM_MESSAGE_LIMIT for r in replies)
    joined = "".join(replies)
    assert all(f"Задача {i} " in joined for i in range(30))


async def test_list_csv_empty(make_message):
    message = make_message("/list_csv")
    await tasks.cmd_list_csv(message)
    message.answer_document.assert_not_awaited()


async def test_list_csv_sends_file_and_removes_it(make_message, isolated_db):
    isolated_db.add_task("Задача", "anna")
    message = make_message("/list_csv")
    await tasks.cmd_list_csv(message)
    message.answer_document.assert_awaited_once()
    sent_file = message.answer_document.call_args.args[0]
    assert "1 шт." in message.answer_document.call_args.kwargs["caption"]
    # Временный CSV удалён после отправки
    from pathlib import Path

    assert not Path(sent_file.path).exists()


def test_split_keeps_short_text_in_one_message():
    assert split_into_messages(["a", "b"]) == ["a\nb"]


def test_split_respects_limit():
    blocks = ["x" * 6, "y" * 6, "z" * 6]
    result = split_into_messages(blocks, limit=13)
    assert result == ["xxxxxx\nyyyyyy", "zzzzzz"]


def test_split_cuts_single_oversized_block():
    result = split_into_messages(["x" * 25], limit=10)
    assert result == ["x" * 10, "x" * 10, "x" * 5]


def test_split_empty_list():
    assert split_into_messages([]) == []
