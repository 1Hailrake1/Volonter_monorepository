from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ============= BASE =============
class SkillBase(BaseModel):
    """Базовая схема навыка"""
    name: str = Field(..., min_length=2, max_length=100, description="Название навыка")


# ============= CREATE =============
class SkillCreate(SkillBase):
    """Создание навыка (только админ)"""
    description: Optional[str] = Field(None, description="Описание навыка")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Организация мероприятий",
                "description": "Умение планировать и координировать события"
            }
        }
    )


# ============= UPDATE =============
class SkillUpdate(BaseModel):
    """Обновление навыка (partial, только админ)"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


# ============= READ =============
class SkillRead(BaseModel):
    """Чтение навыка"""
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class SkillListResponse(BaseModel):
    """Список всех навыков (для справочника)"""
    skills: list[SkillRead]
    total: int