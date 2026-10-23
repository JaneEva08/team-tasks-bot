"""Тесты работы с базой задач."""
import csv
import sqlite3

from database.db import Database


def test_empty_database_has_no_tasks(database):
    assert database.get_all_tasks() == []


def test_add_task_returns_increasing_ids(database):
    first = database.add_task("Подготовить отчёт", "anna")
    second = database.add_task("Созвон с заказчиком", "boris")
    assert second == first + 1


def test_tasks_are_returned_in_order_of_adding(database):
    database.add_task("Первая", "anna")
    database.add_task("Вторая", "boris")
    tasks = database.get_all_tasks()
    assert [t[1] for t in tasks] == ["Первая", "Вторая"]
    assert [t[2] for t in tasks] == ["anna", "boris"]


def test_tasks_survive_reopening(tmp_path):
    # Имитация перезапуска бота: новый объект Database на тот же файл
    path = tmp_path / "tasks.db"
    Database(path).add_task("Не потеряться", "anna")
    assert Database(path).get_all_tasks()[0][1] == "Не потеряться"


def test_database_creates_missing_folder(tmp_path):
    # В Docker база лежит в /app/data — папки может ещё не быть
    path = tmp_path / "data" / "nested" / "tasks.db"
    Database(path).add_task("Задача", "anna")
    assert path.exists()


def test_special_characters_are_stored_as_is(database):
    # Параметризованный запрос: кавычки и SQL не ломают запись
    text = "Robert'); DROP TABLE tasks;-- «ёлка» 🎄"
    database.add_task(text, "anna")
    assert database.get_all_tasks()[0][1] == text


def test_empty_text_is_rejected_by_database(database):
    # Защита на уровне схемы: text NOT NULL
    try:
        database.add_task(None, "anna")
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("ожидали IntegrityError")


def test_export_to_csv_writes_header_and_rows(database):
    database.add_task("Задача с запятой, и кавычкой \"x\"", "anna")
    file_path = database.export_to_csv()
    try:
        with open(file_path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["ID", "Текст задачи", "Автор", "Дата создания"]
        assert rows[1][1] == "Задача с запятой, и кавычкой \"x\""
        assert len(rows) == 2
    finally:
        file_path.unlink()


def test_export_uses_bom_for_excel(database):
    # utf-8-sig — чтобы Excel открывал кириллицу без кракозябр
    database.add_task("Кириллица", "anna")
    file_path = database.export_to_csv()
    try:
        assert file_path.read_bytes().startswith(b"\xef\xbb\xbf")
    finally:
        file_path.unlink()
