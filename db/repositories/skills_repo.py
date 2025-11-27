from sqlalchemy import select, delete, update, func
from typing import List

from models.orm_db_models.tables import Skills
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.skill_dto import (
    SkillRead,
    SkillCreate,
    SkillUpdate,
    SkillListResponse
)


@register_repository("skills")
class SkillsRepo(BaseRepo):

    async def get_all_skills(self) -> List[SkillRead]:
        """Получает список всех навыков."""
        stmt = select(Skills)
        result = await self.session.execute(stmt)
        skills_orm = result.scalars().all()
        return [SkillRead.from_orm(skill) for skill in skills_orm]

    async def get_skill_by_id(self, skill_id: int) -> SkillRead | None:
        """Получает навык по ID."""
        skill = await self.session.get(Skills, skill_id)
        return SkillRead.from_orm(skill) if skill else None

    async def create_skill(self, skill_in: SkillCreate) -> SkillRead:
        """Создает новый навык."""
        skill_orm = Skills(**skill_in.model_dump())
        self.session.add(skill_orm)
        await self.session.flush()
        return SkillRead.from_orm(skill_orm)

    async def update_skill(self, skill_id: int, skill_in: SkillUpdate) -> SkillRead | None:
        """Обновляет навык."""
        skill = await self.session.get(Skills, skill_id)
        if not skill:
            return None

        update_data = skill_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(skill, key, value)

        return SkillRead.from_orm(skill)

    async def delete_skill(self, skill_id: int) -> int:
        """Удаляет навык."""
        stmt = delete(Skills).where(Skills.id == skill_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_skills_by_ids(self, skill_ids: List[int]) -> List[SkillRead]:
        """Получает список навыков по списку ID."""
        stmt = select(Skills).where(Skills.id.in_(skill_ids))
        result = await self.session.execute(stmt)
        skills_orm = result.scalars().all()
        return [SkillRead.from_orm(skill) for skill in skills_orm]

    async def get_paginated_skills(self, page: int, page_size: int) -> SkillListResponse:
        """Пагинированный список навыков."""
        # Count total
        count_stmt = select(func.count()).select_from(Skills)
        total = await self.session.scalar(count_stmt) or 0

        # Get page
        offset = (page - 1) * page_size
        stmt = select(Skills).limit(page_size).offset(offset)
        result = await self.session.execute(stmt)
        skills_orm = result.scalars().all()

        return SkillListResponse(
            skills=[SkillRead.from_orm(s) for s in skills_orm],
            total=total,
            page=page,
            page_size=page_size
        )
