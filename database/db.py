"""
Модуль для работы с базой данных SQLite3.
Хранит все задачи в файле tasks.db в таблице tasks.
"""
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "tasks.db"


class Database:
    """Класс инкапсулирует всю работу с базой данных задач."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        # Открываем новое соединение на каждый запрос — просто и безопасно
        # для небольшого бота без конкурентной записи из разных потоков.
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        # Создаём таблицу tasks, если она ещё не существует.
        conn = self._connect()
        try:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT NOT NULL,
                        user TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
        finally:
            conn.close()  # `with conn` коммитит транзакцию, но не закрывает соединение

    def add_task(self, text: str, user: str) -> int:
        """Добавляет новую задачу в базу и возвращает её id."""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self._connect()
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO tasks (text, user, created_at) VALUES (?, ?, ?)",
                    (text, user, created_at),
                )
                return cursor.lastrowid
        finally:
            conn.close()

    def get_all_tasks(self) -> list[tuple]:
        """Возвращает все задачи в порядке добавления (от старых к новым)."""
        conn = self._connect()
        try:
            cursor = conn.execute(
                "SELECT id, text, user, created_at FROM tasks ORDER BY id ASC"
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def export_to_csv(self) -> Path:
        """Выгружает все задачи в CSV-файл и возвращает путь к нему."""
        tasks = self.get_all_tasks()
        filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = Path(filename)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["ID", "Текст задачи", "Автор", "Дата создания"])
            for task in tasks:
                writer.writerow(task)

        return file_path
