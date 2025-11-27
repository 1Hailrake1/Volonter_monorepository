from sqlalchemy import select, delete, update, func
from typing import List

from models.orm_db_models.tables import Tags
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.tag_dto import (
    TagRead,
    TagCreate,
    TagUpdate,
    TagListResponse
)


@register_repository("tags")
class TagsRepo(BaseRepo):

    async def get_all_tags(self) -> List[TagRead]:
        """Получает список всех тегов."""
        stmt = select(Tags)
        result = await self.session.execute(stmt)
        tags_orm = result.scalars().all()
        return [TagRead.from_orm(tag) for tag in tags_orm]

    async def get_tag_by_id(self, tag_id: int) -> TagRead | None:
        """Получает тег по ID."""
        tag = await self.session.get(Tags, tag_id)
        return TagRead.from_orm(tag) if tag else None

    async def create_tag(self, tag_in: TagCreate) -> TagRead:
        """Создает новый тег."""
        tag_orm = Tags(**tag_in.model_dump())
        self.session.add(tag_orm)
        await self.session.flush()
        return TagRead.from_orm(tag_orm)

    async def update_tag(self, tag_id: int, tag_in: TagUpdate) -> TagRead | None:
        """Обновляет тег."""
        tag = await self.session.get(Tags, tag_id)
        if not tag:
            return None

        update_data = tag_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tag, key, value)

        return TagRead.from_orm(tag)

    async def delete_tag(self, tag_id: int) -> int:
        """Удаляет тег."""
        stmt = delete(Tags).where(Tags.id == tag_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_tags_by_ids(self, tag_ids: List[int]) -> List[TagRead]:
        """Получает список тегов по списку ID."""
        stmt = select(Tags).where(Tags.id.in_(tag_ids))
        result = await self.session.execute(stmt)
        tags_orm = result.scalars().all()
        return [TagRead.from_orm(tag) for tag in tags_orm]

    async def get_paginated_tags(self, page: int, page_size: int) -> TagListResponse:
        """Пагинированный список тегов."""
        count_stmt = select(func.count()).select_from(Tags)
        total = await self.session.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = select(Tags).limit(page_size).offset(offset)
        result = await self.session.execute(stmt)
        tags_orm = result.scalars().all()

        return TagListResponse(
            tags=[TagRead.from_orm(t) for t in tags_orm],
            total=total,
            page=page,
            page_size=page_size
        )
