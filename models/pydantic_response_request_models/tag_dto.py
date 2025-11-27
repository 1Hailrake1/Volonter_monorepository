from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ============= BASE =============
class TagBase(BaseModel):
    """Базовая схема тега"""
    name: str = Field(..., min_length=2, max_length=100, description="Название тега")


# ============= CREATE =============
class TagCreate(TagBase):
    """Создание тега (только админ)"""
    description: Optional[str] = Field(None, description="Описание категории")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Благотворительность",
                "description": "Помощь нуждающимся"
            }
        }
    )


# ============= UPDATE =============
class TagUpdate(BaseModel):
    """Обновление тега (partial, только админ)"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


# ============= READ =============
class TagRead(BaseModel):
    """Чтение тега"""
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class TagListResponse(BaseModel):
    """Список всех тегов (для справочника)"""
    tags: list[TagRead]
    total: int