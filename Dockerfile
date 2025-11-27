FROM python:3.10-bullseye

ENV ACCEPT_EULA=Y \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      unixodbc unixodbc-dev libodbc1 odbcinst \
      ca-certificates curl gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY msodbcsql17_17.10.5.1-1_amd64.deb /tmp/msodbcsql17.deb
RUN set -eux; \
    dpkg -i /tmp/msodbcsql17.deb || apt-get -y -f install; \
    rm -f /tmp/msodbcsql17.deb; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8081

# Два процесса gunicorn (uvicorn worker)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", \
     "--workers", "4", "--bind", "0.0.0.0:8081"]