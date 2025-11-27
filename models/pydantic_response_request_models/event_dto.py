from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Импорты из других DTO
from models.pydantic_response_request_models.skill_dto import SkillRead
from models.pydantic_response_request_models.tag_dto import TagRead
from models.pydantic_response_request_models.user_dto import OrganizerRead


# ============= ENUMS =============
class EventStatus(str, Enum):
    """Статусы события"""
    PENDING = "pending"  # Ожидает одобрения админом
    APPROVED = "approved"  # Одобрено, идет набор волонтеров
    CANCELED = "canceled"  # Отменено организатором
    COMPLETED = "completed"  # Завершено (автоматически после end_date)


# ============= BASE =============
class EventBase(BaseModel):
    """Базовые поля события"""
    title: str = Field(..., min_length=5, max_length=255, description="Название мероприятия")
    description: str = Field(..., min_length=20, description="Подробное описание")
    location: str = Field(..., max_length=255, description="Место проведения")
    required_volunteers: int = Field(..., ge=1, le=1000, description="Требуется волонтеров")
    start_date: datetime = Field(..., description="Дата и время начала")
    end_date: datetime = Field(..., description="Дата и время окончания")
    contact_info: Optional[str] = Field(None, description="Контакты организатора (email, telegram)")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v: datetime, info) -> datetime:
        """Проверка что end_date > start_date"""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('Дата окончания должна быть позже даты начала')
        return v


# ============= CREATE =============
class EventCreate(EventBase):
    """Создание события (только организатор)"""
    tag_ids: List[int] = Field(default_factory=list, description="ID тегов мероприятия")
    skill_ids: List[int] = Field(default_factory=list, description="ID требуемых навыков")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Уборка парка Горького",
                "description": "Приглашаем волонтеров на уборку территории парка. Нужно убрать мусор, подмести дорожки.",
                "location": "Москва, Парк Горького",
                "required_volunteers": 15,
                "start_date": "2025-12-01T10:00:00",
                "end_date": "2025-12-01T16:00:00",
                "contact_info": "t.me/park_cleanup",
                "tag_ids": [1, 2],
                "skill_ids": [5]
            }
        }
    )


# ============= UPDATE =============
class EventUpdate(BaseModel):
    """Обновление события (partial, только организатор)"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    location: Optional[str] = Field(None, max_length=255)
    required_volunteers: Optional[int] = Field(None, ge=1, le=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    contact_info: Optional[str] = None
    event_image_url: Optional[str] = Field(None, max_length=500)
    tag_ids: Optional[List[int]] = None  # Для обновления тегов
    skill_ids: Optional[List[int]] = None  # Для обновления навыков


class EventStatusUpdate(BaseModel):
    """Обновление статуса события (только админ или организатор)"""
    status: EventStatus

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "approved"
            }
        }
    )


# ============= READ =============
class EventRead(EventBase):
    """Базовое чтение события"""
    id: int
    organizer_id: int
    status: EventStatus
    event_image_url: Optional[str] = None
    date_created: datetime
    date_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EventWithDetails(EventRead):
    """Событие с полной информацией (для детальной страницы)"""
    organizer: OrganizerRead
    tags: List[TagRead] = Field(default_factory=list)
    required_skills: List[SkillRead] = Field(default_factory=list)
    # Computed fields (считаются в сервисе)
    applications_count: int = Field(0, description="Количество заявок")
    approved_volunteers_count: int = Field(0, description="Одобрено волонтеров")

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class EventListItem(BaseModel):
    """Элемент списка событий (для карточки на главной)"""
    id: int
    title: str
    location: str
    start_date: datetime
    end_date: datetime
    required_volunteers: int
    status: EventStatus
    event_image_url: Optional[str] = None
    organizer: OrganizerRead
    tags: List[TagRead] = Field(default_factory=list)
    # Computed
    approved_volunteers_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class EventFilters(BaseModel):
    """Фильтры для поиска событий"""
    location: Optional[str] = Field(None, description="Фильтр по городу")
    tag_ids: Optional[List[int]] = Field(None, description="Фильтр по тегам")
    skill_ids: Optional[List[int]] = Field(None, description="Фильтр по навыкам")
    status: Optional[EventStatus] = Field(None, description="Фильтр по статусу")
    start_date_from: Optional[datetime] = Field(None, description="События начинающиеся после")
    start_date_to: Optional[datetime] = Field(None, description="События начинающиеся до")
    organizer_id: Optional[int] = Field(None, description="Фильтр по организатору")
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class EventListResponse(BaseModel):
    """Пагинированный список событий"""
    events: List[EventListItem]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Вычисляемое поле - всего страниц"""
        return (self.total + self.page_size - 1) // self.page_size