FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Установка только PostgreSQL библиотек (остальное уже есть в полном образе)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Копируем и настраиваем entrypoint скрипт
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Создаем директорию для логов и секретов
RUN mkdir -p /app/logger/logs /app/app/security/secrets

# Открываем порт
EXPOSE 8060

# Используем entrypoint для генерации ключей при каждом запуске
ENTRYPOINT ["docker-entrypoint.sh"]

# Запуск с uvicorn в 4 воркера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8060", "--workers", "1"]