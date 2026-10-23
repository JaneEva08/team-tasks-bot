"""Общие настройки тестов.

Тесты не ходят в Telegram и не требуют токена: сообщения бота подменяются
заглушками, а база создаётся во временной папке для каждого теста.
"""
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

# База по умолчанию — во временной папке, чтобы импорт пакета database
# не создавал tasks.db рядом с кодом.
os.environ.setdefault("DB_PATH", str(Path(tempfile.mkdtemp()) / "test_tasks.db"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import Database  # noqa: E402


@pytest.fixture
def database(tmp_path):
    """Чистая база в отдельном файле для каждого теста."""
    return Database(tmp_path / "tasks.db")


@pytest.fixture
def make_message():
    """Фабрика заглушек входящего сообщения Telegram."""

    def _make(text=None, username="anna", full_name="Анна Тестова"):
        return SimpleNamespace(
            text=text,
            from_user=SimpleNamespace(username=username, full_name=full_name),
            answer=AsyncMock(),
            answer_document=AsyncMock(),
        )

    return _make


@pytest.fixture
def state():
    """Заглушка FSM-состояния aiogram."""
    return AsyncMock()
