FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей для PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для логов
RUN mkdir -p /app/logger/logs

# Открываем порт
EXPOSE 8060

# Запуск с uvicorn в 4 воркера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8060", "--workers", "4"]