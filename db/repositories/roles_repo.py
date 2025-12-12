from sqlalchemy import select, delete, insert
from typing import List

from models.orm_db_models.tables import Roles, RolesInfo
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.role_dto import (
    RoleRead,
    RoleListResponse
)


@register_repository("roles")
class RolesRepo(BaseRepo):

    async def get_all_roles(self) -> RoleListResponse:
        """Получает список всех доступных ролей."""
        stmt = select(RolesInfo)
        result = await self.session.execute(stmt)
        roles_orm = result.scalars().all()
        
        roles_list = [RoleRead.from_orm(role) for role in roles_orm]
        return RoleListResponse(roles=roles_list, total=len(roles_list))

    async def get_role_by_id(self, role_id: int) -> RoleRead | None:
        """Получает роль по ID."""
        role = await self.session.get(RolesInfo, role_id)
        return RoleRead.from_orm(role) if role else None

    async def get_role_by_name(self, role_name: str) -> RoleRead | None:
        """Получает роль по названию."""
        stmt = select(RolesInfo).where(RolesInfo.role_name == role_name)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        return RoleRead.from_orm(role) if role else None

    async def add_role_to_user(self, user_id: int, role_id: int) -> bool:
        """Добавляет роль пользователю."""
        stmt = select(Roles).where(Roles.user_id == user_id, Roles.role_id == role_id)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            return False  # Уже есть

        stmt = insert(Roles).values(user_id=user_id, role_id=role_id)
        await self.session.execute(stmt)
        return True

    async def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Удаляет роль у пользователя."""
        stmt = delete(Roles).where(Roles.user_id == user_id, Roles.role_id == role_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_user_roles(self, user_id: int) -> List[RoleRead]:
        """Получает список ролей пользователя."""
        stmt = (
            select(RolesInfo)
            .join(Roles, Roles.role_id == RolesInfo.id)
            .where(Roles.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        roles_orm = result.scalars().all()
        return [RoleRead.from_orm(role) for role in roles_orm]
