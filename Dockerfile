# Образ Telegram-бота задач команды.
# В образе только код и зависимости: токен передаётся при запуске,
# база лежит в томе /app/data и не попадает в образ.
FROM python:3.12-slim

# Связывает пакет в GitHub Container Registry с репозиторием
LABEL org.opencontainers.image.source="https://github.com/JaneEva08/team-tasks-bot"
LABEL org.opencontainers.image.description="Telegram-бот для задач команды (aiogram 3 + SQLite)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/app/data/tasks.db

WORKDIR /app

# Сначала зависимости — этот слой кэшируется, пока не меняется requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py main.py ./
COPY database/ database/
COPY handlers/ handlers/

# Бот работает не от root: код ему доступен только на чтение, писать можно лишь в /app/data
RUN useradd --create-home --uid 10001 bot \
    && mkdir -p /app/data \
    && chown bot:bot /app/data
USER bot

VOLUME ["/app/data"]

CMD ["python", "main.py"]
