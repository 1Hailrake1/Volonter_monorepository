from http.client import HTTPException


class AppException(Exception):

    def __init__(
            self,
            message:str,
            status_code:int=500,
            error_code:str|None=None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__

        super().__init__(self.message)

'''
Ошибки клиента (4xx)
'''

class NotFoundError(AppException):
    """404 - Ресурс не найден"""
    def __init__(self, message:str = "Ресурс не найден"):
        super().__init__(message, status_code = 404, error_code="NOT FOUND")

class AlreadyExistsError(AppException):
    """400 - Ресурс уже существует"""
    def __init__(self, message: str = "Ресурс уже существует"):
        super().__init__(message, status_code=400, error_code="ALREADY_EXISTS")


class ValidationError(AppException):
    """422 - Ошибка валидации"""
    def __init__(self, message: str = "Ошибка валидации данных"):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")


class UnauthorizedError(AppException):
    """401 - Не авторизован"""
    def __init__(self, message: str = "Требуется авторизация"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class PermissionDeniedError(AppException):
    """403 - Доступ запрещен"""
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(message, status_code=403, error_code="PERMISSION_DENIED")


class BadRequestError(AppException):
    """400 - Некорректный запрос"""
    def __init__(self, message: str = "Некорректный запрос"):
        super().__init__(message, status_code=400, error_code="BAD_REQUEST")

'''
Ошибки сервера (5xx)
'''

class DatabaseError(AppException):
    """500 - Ошибка БД"""
    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message, status_code=500, error_code="DATABASE_ERROR")


class InternalServerError(AppException):
    """500 - Внутренняя ошибка сервера"""
    def __init__(self, message: str = "Внутренняя ошибка сервера"):
        super().__init__(message, status_code=500, error_code="INTERNAL_SERVER_ERROR")


'''
Специфичные ошибки // бизнесовые ошибки
'''
