# Волонтёрская Платформа

> Учебный проект веб-платформы для координации волонтёрской деятельности

## Демо

**Живая демонстрация:** [http://45.10.244.89/](http://45.10.244.89/)

---

## О проекте

Данный репозиторий представляет собой **учебный проект**, разработанный для отработки практических навыков fullstack разработки. Проект не является реальной коммерческой платформой и создан исключительно в образовательных целях.

Волонтёрская платформа реализует базовый функционал для организации волонтёрской деятельности: управление мероприятиями, профили пользователей, регистрация на события и административная панель.

---

## Архитектура

Проект построен на монорепозиторной структуре:

```
volonter_monorepository/
├── app/                    # Основное приложение FastAPI
│   ├── api/               # REST API endpoints
│   ├── core/              # Бизнес-логика
│   ├── services/          # Сервисный слой
│   └── middleware/        # Middleware компоненты
├── models/                # SQLAlchemy модели данных
├── db/                    # Конфигурация базы данных
├── alembic/               # Миграции базы данных
├── logger/                # Модуль логирования
├── frontend/              # React приложение
├── main.py                # Точка входа приложения
├── settings.py            # Конфигурация проекта
└── docker-compose.yml     # Оркестрация контейнеров
```

## Технологический стек

**Backend:**
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- PostgreSQL

**Frontend:**
- React
- JavaScript
- CSS3

**Infrastructure:**
- Docker
- Docker Compose
- Nginx

---

## Установка и запуск

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/1Hailrake1/Volonter_monorepository.git
cd Volonter_monorepository

# Создать файл с переменными окружения
cp .env.example .env

# Запустить все сервисы
docker-compose up -d

# Применить миграции базы данных
docker-compose exec web alembic upgrade head
```

Приложение доступно по адресу: `http://localhost`

API документация: `http://localhost/docs`

---

## Автор

**Hailrake** — Python Backend Developer

- GitHub: [@1Hailrake1](https://github.com/1Hailrake1)
- Демо проект: [http://45.10.244.89/](http://45.10.244.89/)
