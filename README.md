# Telegram-бот для хранения задач команды

Простой Telegram-бот на **Python + aiogram 3 + SQLite3** для сбора и хранения задач/идей команды.

## Возможности

- ✅ Добавление задач в общий список (`/add`)
- 📋 Просмотр всех задач (`/list`)
- 📊 Экспорт задач в CSV-файл (`/list_csv`)
- 💾 Автосохранение в SQLite — данные не теряются при перезапуске бота

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие и список команд |
| `/add` | Добавить новую задачу |
| `/list` | Показать все задачи |
| `/list_csv` | Скачать список задач в формате CSV |

## Структура проекта

```
telegram_task_bot/
├── main.py              # точка входа
├── config.py            # загрузка токена из .env
├── database/
│   └── db.py             # класс Database: создание таблицы, CRUD, экспорт в CSV
├── handlers/
│   ├── start.py           # обработчик /start
│   └── tasks.py           # обработчики /add, /list, /list_csv (+ FSM)
├── requirements.txt
└── .env                  # BOT_TOKEN (не хранится в git)
```

## Установка и запуск

1. Создать и активировать виртуальное окружение:

   ```
   python -m venv venv
   venv\Scripts\Activate.ps1   # Windows PowerShell
   ```

2. Установить зависимости:

   ```
   pip install -r requirements.txt
   ```

3. Создать файл `.env` на основе `.env.example` и вставить токен от [@BotFather](https://t.me/BotFather):

   ```
   BOT_TOKEN=your_token_here
   ```

4. Запустить бота:

   ```
   python main.py
   ```

## База данных

Таблица `tasks` в файле `tasks.db`:

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | уникальный идентификатор задачи |
| text | TEXT | текст задачи |
| user | TEXT | автор задачи |
| created_at | TEXT | дата и время создания |
