from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

# Импорты
from models.pydantic_response_request_models.event_dto import EventListItem
from models.pydantic_response_request_models.user_dto import UserListItem


# ============= BASE =============
class ReviewBase(BaseModel):
    """Базовые поля отзыва"""
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к отзыву")


# ============= CREATE =============
class ReviewCreate(ReviewBase):
    """Создание отзыва"""
    event_id: int = Field(..., description="ID события")
    to_user_id: int = Field(..., description="ID пользователя которому оставляется отзыв")

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Доп проверка рейтинга"""
        if v < 1 or v > 5:
            raise ValueError('Рейтинг должен быть от 1 до 5')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": 10,
                "to_user_id": 5,
                "rating": 5,
                "comment": "Отличный волонтер, очень помог!"
            }
        }
    )


# ============= UPDATE =============
class ReviewUpdate(BaseModel):
    """Обновление отзыва (можно изменить только комментарий и рейтинг)"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


# ============= READ =============
class ReviewRead(ReviewBase):
    """Базовое чтение отзыва"""
    id: int
    event_id: int
    from_user_id: int
    to_user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewWithUsers(ReviewRead):
    """Отзыв с информацией о пользователях"""
    from_user: UserListItem  # Кто оставил
    to_user: UserListItem  # Кому оставлен

    model_config = ConfigDict(from_attributes=True)


class ReviewWithEvent(ReviewRead):
    """Отзыв с информацией о событии"""
    event: EventListItem
    from_user: UserListItem

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class ReviewFilters(BaseModel):
    """Фильтры для списка отзывов"""
    event_id: Optional[int] = Field(None, description="Фильтр по событию")
    from_user_id: Optional[int] = Field(None, description="Кто оставил отзыв")
    to_user_id: Optional[int] = Field(None, description="Кому оставлен отзыв")
    min_rating: Optional[int] = Field(None, ge=1, le=5, description="Минимальный рейтинг")
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ReviewListResponse(BaseModel):
    """Пагинированный список отзывов"""
    reviews: list[ReviewRead]  # или ReviewWithUsers
    total: int
    page: int
    page_size: int
    average_rating: Optional[float] = Field(None, description="Средний рейтинг")

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


# ============= STATISTICS =============
class UserReviewStats(BaseModel):
    """Статистика отзывов пользователя"""
    user_id: int
    total_reviews: int = 0
    average_rating: float = 0.0
    rating_distribution: dict[int, int] = Field(
        default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        description="Распределение оценок"
    )