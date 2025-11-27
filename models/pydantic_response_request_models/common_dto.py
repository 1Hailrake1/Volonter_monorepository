# app/schemas/common_dto.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

# ============= GENERIC TYPES =============
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Универсальный ответ с пагинацией"""
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Вычисляемое поле - всего страниц"""
        return (self.total + self.page_size - 1) // self.page_size


# ============= STANDARD RESPONSES =============
class MessageResponse(BaseModel):
    """Стандартный ответ с сообщением"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Тело ошибки (JSON Payload) - без дублирования HTTP статуса"""
    error_code: str = Field(..., description="Машинно-читаемый код ошибки (NOT_FOUND)")
    detail: str = Field(..., description="Человеко-читаемое сообщение об ошибке")
    path: Optional[str] = Field(None, description="Путь, на котором произошла ошибка")


class SuccessResponse(BaseModel):
    """Успешный ответ без данных"""
    success: bool = True
    message: Optional[str] = None


# ============= HEALTH CHECK =============
class HealthCheckResponse(BaseModel):
    """Ответ health check"""
    status: str  # "ok" или "error"
    database: str  # "connected" или "disconnected"
    version: str = "1.0.0"