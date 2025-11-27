from sqlalchemy import select, delete, update, func, insert
from typing import List, Optional

from models.orm_db_models.tables import Applications, Events, Users
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.application_dto import (
    ApplicationRead,
    ApplicationCreate,
    ApplicationStatus,
    ApplicationListResponse,
    ApplicationWithEvent,
    ApplicationWithVolunteer,
    ApplicationFilters
)
from models.pydantic_response_request_models.event_dto import EventListItem
from models.pydantic_response_request_models.user_dto import UserListItem, OrganizerRead


@register_repository("applications")
class ApplicationsRepo(BaseRepo):

    async def create_application(self, app_in: ApplicationCreate, volunteer_id: int) -> ApplicationRead:
        """Создает новую заявку."""
        app_orm = Applications(**app_in.model_dump(), volunteer_id=volunteer_id)
        self.session.add(app_orm)
        await self.session.flush()
        return ApplicationRead.from_orm(app_orm)

    async def get_application_by_id(self, app_id: int) -> ApplicationRead | None:
        """Получает заявку по ID."""
        app = await self.session.get(Applications, app_id)
        return ApplicationRead.from_orm(app) if app else None

    async def update_application_status(self, app_id: int, status: ApplicationStatus) -> bool:
        """Обновляет статус заявки."""
        stmt = update(Applications).where(Applications.id == app_id).values(status=status)
        result = await self.session.execute(stmt)
        return result.rowcount == 1

    async def bulk_approve_applications(self, app_ids: List[int]) -> int:
        """Массовое одобрение заявок."""
        stmt = (
            update(Applications)
            .where(Applications.id.in_(app_ids))
            .values(status=ApplicationStatus.APPROVED)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def bulk_reject_applications(self, app_ids: List[int]) -> int:
        """Массовое отклонение заявок."""
        stmt = (
            update(Applications)
            .where(Applications.id.in_(app_ids))
            .values(status=ApplicationStatus.REJECTED)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_paginated_applications(self, filters: ApplicationFilters) -> ApplicationListResponse:
        """Пагинированный список заявок."""
        query = select(Applications)

        if filters.event_id:
            query = query.where(Applications.event_id == filters.event_id)
        if filters.volunteer_id:
            query = query.where(Applications.volunteer_id == filters.volunteer_id)
        if filters.status:
            query = query.where(Applications.status == filters.status)

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_stmt) or 0

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.limit(filters.page_size).offset(offset)

        result = await self.session.execute(query)
        apps_orm = result.scalars().all()

        # Enrich data based on context (volunteer or organizer view)
        apps_list = []
        for app in apps_orm:
            # If filtering by volunteer, we likely want to see event details
            if filters.volunteer_id:
                event = await self.session.get(Events, app.event_id)
                # Need organizer for EventListItem
                organizer = await self.session.get(Users, event.organizer_id)
                organizer_dto = OrganizerRead.from_orm(organizer)
                
                event_dto = EventListItem(
                    **event.__dict__,
                    organizer=organizer_dto,
                    tags=[], # Optimization: skip tags for this list view or fetch if needed
                    approved_volunteers_count=0
                )
                apps_list.append(ApplicationWithEvent(**app.__dict__, event=event_dto))
            
            # If filtering by event, we likely want to see volunteer details
            elif filters.event_id:
                volunteer = await self.session.get(Users, app.volunteer_id)
                volunteer_dto = UserListItem.from_orm(volunteer)
                apps_list.append(ApplicationWithVolunteer(**app.__dict__, volunteer=volunteer_dto))
            
            # Default fallback
            else:
                apps_list.append(ApplicationRead.from_orm(app))

        return ApplicationListResponse(
            applications=apps_list,
            total=total,
            page=filters.page,
            page_size=filters.page_size
        )
