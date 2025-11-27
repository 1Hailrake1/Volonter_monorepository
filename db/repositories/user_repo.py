
from sqlalchemy import delete, select, update, func
from sqlalchemy.orm import selectinload

from models.orm_db_models.tables import Users, Roles, RolesInfo, Applications, Events, Reviews, Skills, UserSkills
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.user_dto import (
    UserRead,
    UserUpdate,
    UserPublic,
    UserInDB,
    UserPasswordChange,
    UserListResponse,  # ВАЖНО: для вашей задачи
    UserListItem, UserRegister,
    UserCabinetInfo, UserStatistics, UserEventsInfo, RoleRead
)
from models.pydantic_response_request_models.skill_dto import SkillRead


@register_repository("users")
class UserRepo(BaseRepo):

    async def get_user(self, user_id: int) -> UserRead | None:
        """Получает пользователя по ID и возвращает UserRead."""
        data = await self.session.get(Users, user_id)
        return UserRead.from_orm(data) if data else None

    async def create_user(self, user_in: UserRegister) -> UserRead:  # ИСПРАВЛЕНО: на UserInDB
        """Создает нового пользователя (ожидает хешированный пароль)."""
        user_orm = Users(**user_in.model_dump())
        self.session.add(user_orm)
        await self.session.flush()

        return UserRead.from_orm(user_orm)

    async def update_user(self, user_in: UserUpdate) -> UserRead | None:  # Добавлено None в контракт
        """Обновляет поля пользователя по ID."""
        user = await self.session.get(Users, user_in.id)

        if user is None:
            return None  # Репозиторий возвращает None, а Сервис поднимет NotFoundError

        update_data = user_in.model_dump(exclude_unset=True, exclude={"id"})

        for key, value in update_data.items():
            setattr(user, key, value)

        return UserRead.from_orm(user)

    async def delete_by_id(self, user_id: int) -> int:
        """Удаляет пользователя по ID и возвращает количество удаленных строк."""
        stmt = delete(Users).where(Users.id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        """
        Получает пользователя по email (для входа/аутентификации).
        Возвращает UserInDB (внутренняя схема с hashed_password).
        """
        stmt = select(Users).where(Users.email == email)
        result = await self.session.execute(stmt)
        user_orm = result.scalar_one_or_none()

        return UserInDB.from_orm(user_orm) if user_orm else None

    async def change_password(self, user_id: int, new_hashed_password: str) -> bool:
        """
        Обновляет только поле hashed_password для указанного ID.
        Возвращает True, если пароль обновлен (1 строка), иначе False.
        """
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        result = await self.session.execute(stmt)
        return result.rowcount == 1

    async def get_user_public_profile(self, user_id: int) -> UserPublic | None:
        """
        Получает публичную информацию о пользователе (без конфиденциальных полей).
        """
        # Используем session.get, так как получаем по PK, это самый быстрый способ
        user_orm = await self.session.get(Users, user_id)

        return UserPublic.from_orm(user_orm) if user_orm else None

    async def get_total_users_count(self) -> int:
        """Получает общее количество пользователей для пагинации."""
        # Используем func.count() для подсчета строк
        stmt = select(func.count()).select_from(Users)
        total_count = await self.session.scalar(stmt)
        return total_count if total_count is not None else 0

    async def get_paginated_users(self, page: int, page_size: int) -> UserListResponse:
        """
        Возвращает пагинированный список пользователей и общую информацию.
        """
        total_count = await self.get_total_users_count()
        
        offset = (page - 1) * page_size
        
        stmt = select(Users).limit(page_size).offset(offset)
        result = await self.session.execute(stmt)
        users_orm = result.scalars().all()
        
        users_list = [UserListItem.from_orm(user) for user in users_orm]
        
        return UserListResponse(
            users=users_list,
            total=total_count,
            page=page,
            page_size=page_size
        )

    async def exists_user(self, user_email: str) -> bool:
        stmt = select(Users).where(Users.email == user_email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user is not None


    async def get_user_statistics(self, user_id: int) -> UserStatistics:
        """
        Собирает статистику по пользователю.
        """
        # 1. Количество мероприятий, где участвовал (Applications.status == 'approved' и Events.status == 'passed' или просто approved?)
        # Будем считать approved заявки.
        stmt_participated = select(func.count()).select_from(Applications).where(
            Applications.volunteer_id == user_id,
            Applications.status == 'approved'
        )
        participated_count = await self.session.scalar(stmt_participated) or 0

        # 2. Количество организованных мероприятий
        stmt_organized = select(func.count()).select_from(Events).where(
            Events.organizer_id == user_id
        )
        organized_count = await self.session.scalar(stmt_organized) or 0

        # 3. Средний рейтинг (из Reviews, где to_user_id == user_id)
        stmt_rating = select(func.avg(Reviews.rating)).where(Reviews.to_user_id == user_id)
        avg_rating = await self.session.scalar(stmt_rating)

        # 4. Количество отзывов
        stmt_reviews_count = select(func.count()).select_from(Reviews).where(Reviews.to_user_id == user_id)
        reviews_count = await self.session.scalar(stmt_reviews_count) or 0

        return UserStatistics(
            user_id=user_id,
            total_events_participated=participated_count,
            total_events_organized=organized_count,
            average_rating=avg_rating,
            reviews_count=reviews_count
        )

    async def get_user_events(self, user_id: int, role: str = 'volunteer') -> list[UserEventsInfo]:
        """
        Получает список событий пользователя.
        role: 'volunteer' (участвовал) или 'organizer' (организовал)
        """
        if role == 'organizer':
            stmt = select(Events).where(Events.organizer_id == user_id).order_by(Events.start_date.desc())
        else:
            # volunteer - через Applications
            stmt = select(Events).join(Applications, Applications.event_id == Events.id).where(
                Applications.volunteer_id == user_id,
                Applications.status == 'approved' # Только подтвержденные участия
            ).order_by(Events.start_date.desc())

        result = await self.session.execute(stmt)
        events_orm = result.scalars().all()

        return [UserEventsInfo.from_orm(e) for e in events_orm]

    async def get_user_cabinet_info(self, user_id: int) -> UserCabinetInfo | None:
        """
        Получает полную информацию для личного кабинета.
        """
        user = await self.session.get(Users, user_id)
        if not user:
            return None

        # 1. Получаем роли
        stmt_roles = select(RolesInfo).join(Roles, Roles.role_id == RolesInfo.id).where(Roles.user_id == user_id)
        roles_res = await self.session.execute(stmt_roles)
        roles_list = roles_res.scalars().all()

        # 2. Получаем скиллы
        stmt_skills = select(Skills).join(UserSkills, UserSkills.skill_id == Skills.id).where(UserSkills.user_id == user_id)
        skills_res = await self.session.execute(stmt_skills)
        skills_list = skills_res.scalars().all()
        
        # 3. Статистика
        stats = await self.get_user_statistics(user_id)
        
        # 4. События
        events_participated = await self.get_user_events(user_id, role='volunteer')
        events_organized = await self.get_user_events(user_id, role='organizer')

        # Собираем DTO
        # UserCabinetInfo наследуется от UserRead, поэтому нужно заполнить поля UserRead
        user_read = UserRead.from_orm(user)
        
        return UserCabinetInfo(
            **user_read.model_dump(),
            roles=[RoleRead.from_orm(r) for r in roles_list],
            skills=[SkillRead.from_orm(s) for s in skills_list],
            statistics=stats,
            events_participated=events_participated,
            events_organized=events_organized
        )

    async def reactivate_user(self, user_id: int) -> bool:
        stmt = update(Users).where(Users.id == user_id).values(is_active=True)
        result = await self.session.execute(stmt)
        return result.rowcount == 1

    async def set_user_active_status(self, user_id: int, is_active: bool) -> bool:
        stmt = update(Users).where(Users.id == user_id).values(is_active=is_active)
        result = await self.session.execute(stmt)
        return result.rowcount == 1
