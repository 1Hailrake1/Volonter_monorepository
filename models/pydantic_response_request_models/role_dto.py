from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


# ============= ENUMS =============
class RoleName(str, Enum):
    """Системные роли"""
    ADMIN = "admin"
    USER = "user"
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"


# ============= BASE =============
class RoleBase(BaseModel):
    """Базовая схема роли"""
    role_name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


# ============= CREATE =============
class RoleCreate(RoleBase):
    """Создание роли (только админ, редко используется)"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role_name": "moderator",
                "description": "Модератор платформы"
            }
        }
    )


# ============= READ =============
class RoleRead(BaseModel):
    """Чтение роли"""
    id: int
    role_name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class RoleListResponse(BaseModel):
    """Список всех ролей"""
    roles: list[RoleRead]
    total: int