from app.core.exceptions import NotFoundError, PermissionDeniedError, AlreadyExistsError, BadRequestError
from app.services.services_factory import BaseService, register_services
from db.repositories.applications_repo import ApplicationsRepo
from db.repositories.events_repo import EventsRepo
from models.pydantic_response_request_models.application_dto import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatus,
    ApplicationFilters,
    ApplicationListResponse,
    ApplicationBulkApprove,
    ApplicationBulkReject
)
from sqlalchemy.exc import IntegrityError


@register_services("applications")
class ApplicationService(BaseService):
    
    async def create_application(self, app_data: ApplicationCreate, volunteer_id: int) -> ApplicationRead:
        """Создаёт заявку на участие в мероприятии"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            applications_repo: ApplicationsRepo = self.uow.applications
            
            # Проверяем, что мероприятие существует и имеет статус approved
            event = await events_repo.get_event_by_id(app_data.event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {app_data.event_id} не найдено")
            
            if event.status != "approved":
                raise BadRequestError("Нельзя подать заявку на неодобренное мероприятие")
            
            # Проверяем, что волонтёр не является организатором
            if event.organizer_id == volunteer_id:
                raise BadRequestError("Организатор не может подать заявку на своё мероприятие")
            
            try:
                new_application = await applications_repo.create_application(app_data, volunteer_id)
                await self.uow.commit()
                return new_application
            except IntegrityError:
                raise AlreadyExistsError("Вы уже подали заявку на это мероприятие")
    
    async def get_application_by_id(self, app_id: int) -> ApplicationRead:
        """Получает заявку по ID"""
        async with self.uow:
            applications_repo: ApplicationsRepo = self.uow.applications
            application = await applications_repo.get_application_by_id(app_id)
            if not application:
                raise NotFoundError(f"Заявка с ID {app_id} не найдена")
            return application
    
    async def update_application_status(
        self, 
        app_id: int, 
        status: ApplicationStatus, 
        user_id: int
    ) -> dict:
        """
        Обновляет статус заявки.
        Организатор может одобрить/отклонить (approved/rejected).
        Волонтёр может отменить свою заявку (canceled).
        """
        async with self.uow:
            applications_repo: ApplicationsRepo = self.uow.applications
            events_repo: EventsRepo = self.uow.events
            
            application = await applications_repo.get_application_by_id(app_id)
            if not application:
                raise NotFoundError(f"Заявка с ID {app_id} не найдена")
            
            # Получаем мероприятие для проверки прав
            event = await events_repo.get_event_by_id(application.event_id)
            
            # Проверка прав
            if status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]:
                # Одобрить/отклонить может только организатор мероприятия
                if event.organizer_id != user_id:
                    raise PermissionDeniedError("Только организатор может изменять статус заявки")
            elif status == ApplicationStatus.CANCELED:
                # Отменить может только волонтёр, подавший заявку
                if application.volunteer_id != user_id:
                    raise PermissionDeniedError("Вы можете отменить только свою заявку")
            else:
                raise BadRequestError(f"Недопустимый статус: {status}")
            
            success = await applications_repo.update_application_status(app_id, status)
            await self.uow.commit()
            
            return {"message": f"Статус заявки изменён на {status}", "success": success}
    
    async def get_my_applications(self, volunteer_id: int, page: int = 1, page_size: int = 20) -> ApplicationListResponse:
        """Получает все заявки волонтёра"""
        async with self.uow:
            applications_repo: ApplicationsRepo = self.uow.applications
            filters = ApplicationFilters(volunteer_id=volunteer_id, page=page, page_size=page_size)
            applications = await applications_repo.get_paginated_applications(filters)
            return applications
    
    async def get_event_applications(
        self, 
        event_id: int, 
        organizer_id: int,
        status: ApplicationStatus = None,
        page: int = 1,
        page_size: int = 20
    ) -> ApplicationListResponse:
        """Получает все заявки на мероприятие (только для организатора)"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            applications_repo: ApplicationsRepo = self.uow.applications
            
            # Проверяем, что пользователь - организатор этого мероприятия
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            
            if event.organizer_id != organizer_id:
                raise PermissionDeniedError("Вы можете просматривать заявки только на свои мероприятия")
            
            filters = ApplicationFilters(
                event_id=event_id,
                status=status,
                page=page,
                page_size=page_size
            )
            applications = await applications_repo.get_paginated_applications(filters)
            return applications
    
    async def bulk_approve_applications(self, data: ApplicationBulkApprove, organizer_id: int) -> dict:
        """Массовое одобрение заявок (только организатор)"""
        async with self.uow:
            applications_repo: ApplicationsRepo = self.uow.applications
            events_repo: EventsRepo = self.uow.events
            
            # Проверяем права для каждой заявки (берём первую для проверки мероприятия)
            if data.application_ids:
                first_app = await applications_repo.get_application_by_id(data.application_ids[0])
                if first_app:
                    event = await events_repo.get_event_by_id(first_app.event_id)
                    if event.organizer_id != organizer_id:
                        raise PermissionDeniedError("Вы можете одобрять заявки только на свои мероприятия")
            
            approved_count = await applications_repo.bulk_approve_applications(data.application_ids)
            await self.uow.commit()
            
            return {
                "message": f"Одобрено заявок: {approved_count}",
                "approved_count": approved_count
            }
    
    async def bulk_reject_applications(self, data: ApplicationBulkReject, organizer_id: int) -> dict:
        """Массовое отклонение заявок (только организатор)"""
        async with self.uow:
            applications_repo: ApplicationsRepo = self.uow.applications
            events_repo: EventsRepo = self.uow.events
            
            # Проверяем права
            if data.application_ids:
                first_app = await applications_repo.get_application_by_id(data.application_ids[0])
                if first_app:
                    event = await events_repo.get_event_by_id(first_app.event_id)
                    if event.organizer_id != organizer_id:
                        raise PermissionDeniedError("Вы можете отклонять заявки только на свои мероприятия")
            
            rejected_count = await applications_repo.bulk_reject_applications(data.application_ids)
            await self.uow.commit()
            
            return {
                "message": f"Отклонено заявок: {rejected_count}",
                "rejected_count": rejected_count
            }
