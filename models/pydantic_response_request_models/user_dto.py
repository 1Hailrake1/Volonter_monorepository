from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime

# Импорты других dto
from models.pydantic_response_request_models.role_dto import RoleRead
from models.pydantic_response_request_models.skill_dto import SkillRead


# ============= USER BASE =============
class UserBase(BaseModel):
    """Базовые поля пользователя"""
    fullname: str = Field(..., min_length=2, max_length=255, description="ФИО пользователя")
    email: EmailStr = Field(..., description="Email для входа")
    location: Optional[str] = Field(None, max_length=255, description="Город")
    date_birth: Optional[datetime] = Field(None, description="Дата рождения")

    model_config = ConfigDict(from_attributes=True)

# ============= REGISTRATION / AUTH =============
class UserRegister(BaseModel):
    """Регистрация нового пользователя"""
    fullname: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    hashed_password: str = Field(..., min_length=8, description="Минимум 8 символов")
    location: Optional[str] = Field(None, max_length=255)
    date_birth: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "fullname": "Иван Иванов",
                "email": "ivan@example.com",
                "hashed_password": "SecurePass123",
                "location": "Москва",
                "date_birth": "1995-03-15T00:00:00"
            }
        }
    )


class UserLogin(BaseModel):
    """Вход пользователя"""
    email: EmailStr
    hashed_password: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "ivan@example.com",
                "hashed_password": "SecurePass123"
            }
        }
    )


# ============= UPDATE =============
class UserUpdate(BaseModel):
    """Обновление профиля (все поля опциональны)"""
    id: int = Field(..., description="ID пользователя для обновления")
    fullname: Optional[str] = Field(None, min_length=2, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    date_birth: Optional[datetime] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    roles: List[RoleRead] = Field(default_factory=list)
    skills: List[SkillRead] = Field(default_factory=list)
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "fullname": "Иван Петров",
                "location": "Санкт-Петербург",
                "date_birth": "1995-03-15T00:00:00",
                "avatar_url": "https://avatars.githubusercontent.com",
                "roles": ["admin", "organizator"],
                "skills": ["read"]
            }
        }
    )


class UserPasswordChange(BaseModel):
    """Смена пароля"""
    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")

    model_config = ConfigDict(from_attributes=True)

# ============= READ =============
class UserRead(UserBase):
    """Базовое чтение пользователя (публичная информация)"""
    id: int
    avatar_url: Optional[str] = None
    date_created: datetime
    is_active: bool


class UserWithSkills(UserRead):
    """Пользователь с навыками"""
    skills: List[SkillRead] = Field(default_factory=list)


class UserWithRoles(UserRead):
    """Пользователь с ролями"""
    roles: List[RoleRead] = Field(default_factory=list)


class UserProfile(UserRead):
    """Полный профиль пользователя (для владельца)"""
    skills: List[SkillRead] = Field(default_factory=list)
    roles: List[RoleRead] = Field(default_factory=list)
    date_last_login: Optional[datetime] = None


# ============= PUBLIC PROFILE =============
class UserPublic(BaseModel):
    """Публичный профиль (для других пользователей)"""
    id: int
    fullname: str
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    skills: List[SkillRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ============= LIST =============
class UserListItem(BaseModel):
    """Элемент списка пользователей (минимальная инфа)"""
    id: int
    fullname: str
    email: EmailStr
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    date_created: datetime
    roles: List[RoleRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Пагинированный список пользователей"""
    users: List[UserListItem]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Вычисляемое поле - всего страниц"""
        return (self.total + self.page_size - 1) // self.page_size


# ============= INTERNAL (для использования внутри сервера) =============
class UserInDB(UserRead):
    """
    ВНУТРЕННЯЯ схема - НЕ ИСПОЛЬЗОВАТЬ в API responses!
    Содержит конфиденциальные данные
    """
    hashed_password: str
    date_last_login: Optional[datetime] = None


# ============= SKILL MANAGEMENT =============
class UserSkillAdd(BaseModel):
    """Добавление навыка пользователю"""
    skill_ids: List[int] = Field(..., min_length=1, description="ID навыков для добавления")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skill_ids": [1, 3, 5]
            }
        }
    )


class UserSkillRemove(BaseModel):
    """Удаление навыка у пользователя"""
    skill_ids: List[int] = Field(..., min_length=1, description="ID навыков для удаления")


# ============= ROLE MANAGEMENT (только для админа) =============
class UserRoleAdd(BaseModel):
    """Добавление роли пользователю (только админ)"""
    user_id: int
    role_ids: List[int] = Field(..., min_length=1)


class UserRoleRemove(BaseModel):
    """Удаление роли у пользователя (только админ)"""
    user_id: int
    role_ids: List[int] = Field(..., min_length=1)


# ============= STATISTICS (для волонтерской книжки) =============
class UserStatistics(BaseModel):
    """Статистика волонтера (для будущего)"""
    user_id: int
    total_events_participated: int = 0  # Всего мероприятий
    total_events_organized: int = 0  # Организовано мероприятий
    total_hours_volunteered: int = 0  # Всего часов (для будущего)
    average_rating: Optional[float] = None  # Средний рейтинг
    reviews_count: int = 0  # Количество отзывов

    model_config = ConfigDict(from_attributes=True)


class UserTokenInfo(BaseModel):
    """Информация о пользователе из токена"""
    user_id: int
    email: str
    roles: List[RoleRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class UserEventsInfo(BaseModel):
    """Информация о мероприятии для личного кабинета"""
    id: int
    title: str
    location: str
    start_date: datetime
    end_date: datetime
    status: str
    event_image_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserCabinetInfo(UserRead):
    """Полная информация для личного кабинета пользователя"""
    roles: List[RoleRead] = Field(default_factory=list)
    skills: List[SkillRead] = Field(default_factory=list)
    statistics: UserStatistics
    events_participated: List[UserEventsInfo] = Field(default_factory=list)
    events_organized: List[UserEventsInfo] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# ============= ORGANIZER READ (для событий) =============
class OrganizerRead(BaseModel):
    """Минимальная информация об организаторе"""
    id: int
    fullname: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)