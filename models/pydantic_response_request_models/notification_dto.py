from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# ============= ENUMS =============
class NotificationType(str, Enum):
    """Типы уведомлений"""
    EVENT_CREATED = "event_created"  # Создано новое событие (подписчикам тега)
    EVENT_APPROVED = "event_approved"  # Событие одобрено админом
    EVENT_CANCELED = "event_canceled"  # Событие отменено
    EVENT_REMINDER = "event_reminder"  # Напоминание о событии (за 24ч)
    APPLICATION_CREATED = "application_created"  # Новая заявка (организатору)
    APPLICATION_APPROVED = "application_approved"  # Заявка одобрена (волонтеру)
    APPLICATION_REJECTED = "application_rejected"  # Заявка отклонена (волонтеру)
    REVIEW_RECEIVED = "review_received"  # Получен отзыв
    SYSTEM = "system"  # Системное уведомление


# ============= BASE =============
class NotificationBase(BaseModel):
    """Базовые поля уведомления"""
    title: str = Field(..., max_length=255, description="Заголовок уведомления")
    message: str = Field(..., max_length=1000, description="Текст уведомления")
    type: NotificationType = Field(..., description="Тип уведомления")


# ============= CREATE (internal) =============
class NotificationCreate(NotificationBase):
    """Создание уведомления (только внутри сервера)"""
    user_id: int
    related_event_id: Optional[int] = None
    related_application_id: Optional[int] = None


# ============= READ =============
class NotificationRead(NotificationBase):
    """Чтение уведомления"""
    id: int
    user_id: int
    is_read: bool
    related_event_id: Optional[int] = None
    related_application_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============= UPDATE =============
class NotificationMarkAsRead(BaseModel):
    """Пометить уведомление как прочитанное"""
    notification_ids: list[int] = Field(..., min_length=1, description="ID уведомлений")


class NotificationMarkAllAsRead(BaseModel):
    """Пометить все уведомления пользователя как прочитанные"""
    pass  # Пустая схема, user_id берется из токена


# ============= LIST =============
class NotificationFilters(BaseModel):
    """Фильтры для уведомлений"""
    is_read: Optional[bool] = Field(None, description="Только прочитанные/непрочитанные")
    type: Optional[NotificationType] = Field(None, description="Фильтр по типу")
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class NotificationListResponse(BaseModel):
    """Список уведомлений"""
    notifications: list[NotificationRead]
    total: int
    unread_count: int  # Количество непрочитанных
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


# ============= DELETE =============
class NotificationDelete(BaseModel):
    """Удаление уведомлений"""
    notification_ids: list[int] = Field(..., min_length=1, max_length=100)