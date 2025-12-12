from sqlalchemy import select, delete, update, func, insert, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from models.orm_db_models.tables import Events, Users, EventTags, RequiredEventsSkills, Tags, Skills, Applications
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.event_dto import (
    EventRead,
    EventCreate,
    EventUpdate,
    EventListResponse,
    EventListItem,
    EventStatus,
    EventWithDetails,
    EventFilters
)
from models.pydantic_response_request_models.user_dto import OrganizerRead
from models.pydantic_response_request_models.tag_dto import TagRead
from models.pydantic_response_request_models.skill_dto import SkillRead


@register_repository("events")
class EventsRepo(BaseRepo):

    async def get_event_by_id(self, event_id: int) -> EventWithDetails | None:
        """Получает событие по ID с деталями (организатор, теги, навыки)."""
        stmt = (
            select(Events)
            .options(
                selectinload(Events.organizer_id),
            )
            .where(Events.id == event_id)
        )
        event = await self.session.get(Events, event_id)
        if not event:
            return None

        organizer = await self.session.get(Users, event.organizer_id)
        organizer_dto = OrganizerRead.from_orm(organizer)

        tags_stmt = (
            select(Tags)
            .join(EventTags, EventTags.tag_id == Tags.id)
            .where(EventTags.event_id == event_id)
        )
        tags_result = await self.session.execute(tags_stmt)
        tags_list = [TagRead.from_orm(t) for t in tags_result.scalars().all()]

        skills_stmt = (
            select(Skills)
            .join(RequiredEventsSkills, RequiredEventsSkills.skill_id == Skills.id)
            .where(RequiredEventsSkills.event_id == event_id)
        )
        skills_result = await self.session.execute(skills_stmt)
        skills_list = [SkillRead.from_orm(s) for s in skills_result.scalars().all()]
        
        return EventWithDetails(
            **event.__dict__,
            organizer=organizer_dto,
            tags=tags_list,
            required_skills=skills_list,
            applications_count=0,
            approved_volunteers_count=await self._count_approved_volunteers(event_id)
        )

    async def _count_approved_volunteers(self, event_id: int) -> int:
        stmt = select(func.count()).select_from(Applications).where(
            Applications.event_id == event_id,
            Applications.status == 'approved'
        )
        return await self.session.scalar(stmt) or 0

    async def create_event(self, event_in: EventCreate, organizer_id: int) -> EventRead:
        """Создает новое событие."""
        event_data = event_in.model_dump(exclude={"tag_ids", "skill_ids"})
        event_data["organizer_id"] = organizer_id
        
        event_orm = Events(**event_data)
        self.session.add(event_orm)
        await self.session.flush()
        
        # Add tags
        if event_in.tag_ids:
            await self.session.execute(
                insert(EventTags).values(
                    [{"event_id": event_orm.id, "tag_id": tid} for tid in event_in.tag_ids]
                )
            )
            
        # Add skills
        if event_in.skill_ids:
            await self.session.execute(
                insert(RequiredEventsSkills).values(
                    [{"event_id": event_orm.id, "skill_id": sid} for sid in event_in.skill_ids]
                )
            )
            
        return EventRead.from_orm(event_orm)

    async def update_event(self, event_id: int, event_in: EventUpdate) -> EventRead | None:
        """Обновляет событие."""
        event = await self.session.get(Events, event_id)
        if not event:
            return None
            
        update_data = event_in.model_dump(exclude_unset=True, exclude={"tag_ids", "skill_ids"})
        for key, value in update_data.items():
            setattr(event, key, value)

        if event_in.tag_ids is not None:
            await self.session.execute(delete(EventTags).where(EventTags.event_id == event_id))
            if event_in.tag_ids:
                await self.session.execute(
                    insert(EventTags).values(
                        [{"event_id": event_id, "tag_id": tid} for tid in event_in.tag_ids]
                    )
                )

        if event_in.skill_ids is not None:
            await self.session.execute(delete(RequiredEventsSkills).where(RequiredEventsSkills.event_id == event_id))
            if event_in.skill_ids:
                await self.session.execute(
                    insert(RequiredEventsSkills).values(
                        [{"event_id": event_id, "skill_id": sid} for sid in event_in.skill_ids]
                    )
                )

        return EventRead.from_orm(event)

    async def delete_event(self, event_id: int) -> int:
        """Удаляет событие."""
        stmt = delete(Events).where(Events.id == event_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def update_event_status(self, event_id: int, status: EventStatus) -> bool:
        """Обновляет статус события."""
        stmt = update(Events).where(Events.id == event_id).values(status=status)
        result = await self.session.execute(stmt)
        return result.rowcount == 1

    async def get_paginated_events(self, filters: EventFilters) -> EventListResponse:
        """Пагинированный поиск событий с фильтрами."""
        query = select(Events)

        if filters.location:
            query = query.where(Events.location.ilike(f"%{filters.location}%"))
        if filters.status:
            query = query.where(Events.status == filters.status)
        if filters.start_date_from:
            query = query.where(Events.start_date >= filters.start_date_from)
        if filters.start_date_to:
            query = query.where(Events.start_date <= filters.start_date_to)
        if filters.organizer_id:
            query = query.where(Events.organizer_id == filters.organizer_id)

        if filters.tag_ids:
            query = query.join(EventTags).where(EventTags.tag_id.in_(filters.tag_ids)).distinct()

        if filters.skill_ids:
            query = query.join(RequiredEventsSkills).where(RequiredEventsSkills.skill_id.in_(filters.skill_ids)).distinct()

        count_stmt = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_stmt) or 0

        offset = (filters.page - 1) * filters.page_size
        query = query.limit(filters.page_size).offset(offset)
        
        result = await self.session.execute(query)
        events_orm = result.scalars().all()

        events_list = []
        for event in events_orm:
            organizer = await self.session.get(Users, event.organizer_id)
            organizer_dto = OrganizerRead.from_orm(organizer)

            tags_stmt = (
                select(Tags)
                .join(EventTags, EventTags.tag_id == Tags.id)
                .where(EventTags.event_id == event.id)
            )
            tags_res = await self.session.execute(tags_stmt)
            tags_list = [TagRead.from_orm(t) for t in tags_res.scalars().all()]
            
            events_list.append(EventListItem(
                **event.__dict__,
                organizer=organizer_dto,
                tags=tags_list,
                approved_volunteers_count=await self._count_approved_volunteers(event.id)
            ))
            
        return EventListResponse(
            events=events_list,
            total=total,
            page=filters.page,
            page_size=filters.page_size
        )

    async def get_events_by_organizer(self, organizer_id: int) -> List[EventListItem]:
        """Получает все события организатора."""
        stmt = select(Events).where(Events.organizer_id == organizer_id).order_by(Events.start_date.desc())
        result = await self.session.execute(stmt)
        events_orm = result.scalars().all()

        organizer = await self.session.get(Users, organizer_id)
        organizer_dto = OrganizerRead.from_orm(organizer) if organizer else None
        
        events_list = []
        for event in events_orm:
            tags_stmt = (
                select(Tags)
                .join(EventTags, EventTags.tag_id == Tags.id)
                .where(EventTags.event_id == event.id)
            )
            tags_res = await self.session.execute(tags_stmt)
            tags_list = [TagRead.from_orm(t) for t in tags_res.scalars().all()]
            
            events_list.append(EventListItem(
                **event.__dict__,
                organizer=organizer_dto,
                tags=tags_list,
                approved_volunteers_count=await self._count_approved_volunteers(event.id)
            ))
            
        return events_list
