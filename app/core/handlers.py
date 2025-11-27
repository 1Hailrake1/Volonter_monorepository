"""
Глобальные обработчики исключений для FastAPI
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions import AppException
from loguru import logger


# ============= 1. ТВОИ КАСТОМНЫЕ ИСКЛЮЧЕНИЯ =============

def app_exception_handler(
    request: Request,
    exc: AppException
) -> JSONResponse:
    """
    Обработчик ТВОИХ кастомных исключений

    Ловит: NotFoundError, AlreadyExistsError, DatabaseError и т.д.
    """
    logger.warning(
        f"AppException: {exc.error_code} | {exc.message} | "
        f"Path: {request.url.path} | Method: {request.method}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "path": str(request.url.path)
        }
    )


# ============= 2. FASTAPI ВСТРОЕННЫЕ ОШИБКИ =============

def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """
    Обработчик HTTPException от FastAPI

    Ловит:
    - 404 Not Found (несуществующий URL)
    - 405 Method Not Allowed
    - И другие HTTP ошибки от FastAPI

    """
    logger.warning(
        f"HTTPException: {exc.status_code} | {exc.detail} | "
        f"Path: {request.url.path} | Method: {request.method}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )


def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic

    Срабатывает когда клиент отправил невалидные данные
    """
    errors = exc.errors()

    logger.warning(
        f"ValidationError: {len(errors)} errors | "
        f"Path: {request.url.path} | Errors: {errors}"
    )

    # Форматируем ошибки в читаемый вид
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": formatted_errors
        }
    )


# ============= 3. SQLALCHEMY ОШИБКИ =============

def integrity_error_handler(
    request: Request,
    exc: IntegrityError
) -> JSONResponse:
    """
    Обработчик IntegrityError из SQLAlchemy

    Срабатывает при нарушении ограничений БД
    """
    error_msg = str(exc.orig)

    logger.error(
        f"IntegrityError: {error_msg} | "
        f"Path: {request.url.path}",
        exc_info=True
    )

    # Парсим тип ошибки
    if "unique constraint" in error_msg.lower():
        message = "Запись с такими данными уже существует"
        error_code = "UNIQUE_VIOLATION"
    elif "foreign key constraint" in error_msg.lower():
        message = "Связанная запись не найдена"
        error_code = "FOREIGN_KEY_VIOLATION"
    elif "not null constraint" in error_msg.lower():
        message = "Обязательное поле не заполнено"
        error_code = "NOT_NULL_VIOLATION"
    else:
        message = "Ошибка целостности данных"
        error_code = "INTEGRITY_ERROR"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": error_code,
            "message": message
        }
    )


def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Обработчик общих ошибок SQLAlchemy

    Срабатывает при проблемах с БД (connection lost, timeout и т.д.)
    """
    logger.error(
        f"SQLAlchemyError: {str(exc)} | "
        f"Path: {request.url.path}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DATABASE_ERROR",
            "message": "Ошибка при работе с базой данных"
        }
    )


# ============= 4. CATCH-ALL =============

def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Обработчик неожиданных исключений

    Последняя линия защиты
    """
    logger.error(
        f"Unexpected error: {type(exc).__name__} | {str(exc)} | "
        f"Path: {request.url.path}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Произошла непредвиденная ошибка"
        }
    )