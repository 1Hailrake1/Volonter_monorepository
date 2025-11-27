import uvicorn
from logger.logger import logger
from contextlib import asynccontextmanager
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db.manager import db_manager
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions import AppException, NotFoundError
from app.core.handlers import (
    app_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
    integrity_error_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.endpoints import main_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения")

    async with db_manager:
        logger.info("Приложение запущено")
        yield

    logger.info("Приложение остановленно")



app = FastAPI(
    title="Volunteer Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(main_router)


@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all_not_found_route(
        request: Request,
):
    """
    Роутер-заглушка, который перехватывает все пути,
    необработанные другими роутерами.
    Принудительно рейзит вашу NotFoundError.
    """

    raise NotFoundError(message=f"Маршрут '{request.url.path}' не найден")

# Кастомные исключения
app.add_exception_handler(AppException, app_exception_handler)

# 2. FastAPI встроенные исключения
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

# 3. SQLAlchemy исключения
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

# 4. Catch-all (должен быть ПОСЛЕДНИМ!)
app.add_exception_handler(Exception, general_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8060)
