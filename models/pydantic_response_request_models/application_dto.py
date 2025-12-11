from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union
from datetime import datetime
from enum import Enum

# Импорты
from models.pydantic_response_request_models.event_dto import EventListItem
from models.pydantic_response_request_models.user_dto import UserListItem


# ============= ENUMS =============
class ApplicationStatus(str, Enum):
    """Статусы заявки"""
    PENDING = "pending"  # Ожидает рассмотрения
    APPROVED = "approved"  # Одобрена организатором
    REJECTED = "rejected"  # Отклонена организатором
    CANCELED = "canceled"  # Отменена волонтером


# ============= BASE =============
class ApplicationBase(BaseModel):
    """Базовые поля заявки"""
    message: Optional[str] = Field(None, max_length=1000, description="Сопроводительное сообщение")


# ============= CREATE =============
class ApplicationCreate(ApplicationBase):
    """Создание заявки на участие в событии (волонтер)"""
    event_id: int = Field(..., description="ID события")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": 5,
                "message": "Хочу помочь, у меня есть опыт работы с детьми"
            }
        }
    )


# ============= UPDATE =============
class ApplicationStatusUpdate(BaseModel):
    """Обновление статуса заявки (только организатор)"""
    status: ApplicationStatus = Field(..., description="Новый статус")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "approved"
            }
        }
    )


class ApplicationCancel(BaseModel):
    """Отмена заявки волонтером"""
    reason: Optional[str] = Field(None, max_length=500, description="Причина отмены")


# ============= READ =============
class ApplicationRead(ApplicationBase):
    """Базовое чтение заявки"""
    id: int
    event_id: int
    volunteer_id: int
    status: ApplicationStatus
    date_created: datetime
    date_updated: Optional[datetime] = None
    event: Optional["EventListItem"] = None
    volunteer: Optional["UserListItem"] = None

    model_config = ConfigDict(from_attributes=True)


class ApplicationWithEvent(ApplicationRead):
    """Заявка с информацией о событии (для волонтера в "Мои заявки")"""
    event: EventListItem

    model_config = ConfigDict(from_attributes=True)


class ApplicationWithVolunteer(ApplicationRead):
    """Заявка с информацией о волонтере (для организатора)"""
    volunteer: UserListItem

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class ApplicationFilters(BaseModel):
    """Фильтры для списка заявок"""
    event_id: Optional[int] = Field(None, description="Фильтр по событию")
    volunteer_id: Optional[int] = Field(None, description="Фильтр по волонтеру")
    status: Optional[ApplicationStatus] = Field(None, description="Фильтр по статусу")
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ApplicationListResponse(BaseModel):
    """Пагинированный список заявок"""
    applications: list[Union[ApplicationWithEvent, ApplicationWithVolunteer, ApplicationRead]]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


# ============= BULK OPERATIONS =============
class ApplicationBulkApprove(BaseModel):
    """Массовое одобрение заявок (организатор)"""
    application_ids: list[int] = Field(..., min_length=1, max_length=100)


class ApplicationBulkReject(BaseModel):
    """Массовое отклонение заявок (организатор)"""
    application_ids: list[int] = Field(..., min_length=1, max_length=100)
    reason: Optional[str] = Field(None, max_length=500, description="Причина отклонения")