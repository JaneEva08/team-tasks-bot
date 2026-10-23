# Telegram-бот для задач команды

[![Build and Deploy](https://github.com/JaneEva08/team-tasks-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/JaneEva08/team-tasks-bot/actions/workflows/deploy.yml)

Бот на **Python + aiogram 3 + SQLite**: команда добавляет задачи и идеи в общий список, смотрит их и выгружает в CSV для Excel. Проект упакован в Docker, каждое изменение проверяется автотестами в GitHub Actions, готовый образ публикуется в GitHub Container Registry.

## Возможности

- ✅ Добавление задач в общий список (`/add`) с проверкой ввода: фото, стикер или пустое сообщение не ломают бота
- 📋 Просмотр всех задач (`/list`), длинный список приходит несколькими сообщениями
- 📊 Экспорт в CSV (`/list_csv`), кириллица корректно открывается в Excel
- 💾 Задачи хранятся в SQLite и не теряются при перезапуске и обновлении

## Команды

| Команда | Описание |
|---|---|
| `/start` | Приветствие и список команд |
| `/add` | Добавить задачу |
| `/list` | Показать все задачи |
| `/list_csv` | Скачать список в CSV |

## Как устроена доставка (CI/CD)

```
feature/... ──PR──▶ main
   │                 │
   ▼                 ▼
 тесты          тесты → сборка образа → проверка образа → ghcr.io → (сервер)
 пробная сборка
```

- **Pull request в main** — 27 автотестов и пробная сборка Docker-образа. В реестр ничего не уходит.
- **Слияние в main** — тесты, сборка, проверка образа (код запускается, бот не под root, база пишется), публикация в `ghcr.io/janeeva08/team-tasks-bot` с тегами `latest` и `sha-<коммит>`.
- **Деплой на сервер** — готовый job по SSH с откатом на прошлую версию, если контейнер не поднялся. Включается переменной `DEPLOY_ENABLED=true` после настройки сервера.

## Запуск через Docker

На сервере нужны Docker и два файла из репозитория: `docker-compose.yml` и `.env`.

```bash
cp .env.example .env        # вставить токен от @BotFather
docker compose up -d        # скачать образ и запустить
docker compose logs -f      # посмотреть логи
```

Обновление до свежей версии: `docker compose pull && docker compose up -d`.

> ⚠️ `docker compose down -v` удаляет том с базой задач. Для остановки используйте `docker compose down` без `-v`.

Токен в образ не попадает: `.env`, база и выгрузки исключены через `.dockerignore`.

## Запуск без Docker

```bash
python -m venv venv
venv\Scripts\Activate.ps1          # Windows PowerShell; на Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # вставить токен
python main.py
```

## Тесты

```bash
pip install -r requirements-dev.txt
pytest -v
```

Тесты не ходят в Telegram и не требуют токена: сообщения подменяются заглушками, база создаётся во временной папке.

## Настройки

| Переменная | Обязательна | Описание |
|---|---|---|
| `BOT_TOKEN` | да | Токен бота от @BotFather |
| `DB_PATH` | нет | Путь к файлу базы. В Docker — `/app/data/tasks.db` (том) |

## Структура

```
team-tasks-bot/
├── main.py                  # точка входа
├── config.py                # загрузка токена из .env
├── database/db.py           # класс Database: таблица, запись, чтение, CSV
├── handlers/
│   ├── start.py             # /start
│   └── tasks.py             # /add (FSM), /list, /list_csv
├── tests/                   # автотесты pytest
├── Dockerfile               # образ: python:3.12-slim, пользователь без root
├── docker-compose.yml       # запуск на сервере из ghcr.io
└── .github/workflows/
    └── deploy.yml           # тесты → сборка → ghcr.io → деплой
```

## База данных

Таблица `tasks`:

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | идентификатор задачи |
| text | TEXT | текст задачи (до 1000 символов) |
| user | TEXT | автор (username или имя) |
| created_at | TEXT | дата и время создания |
