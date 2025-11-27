from app.core.exceptions import NotFoundError, PermissionDeniedError, BadRequestError
from app.services.services_factory import BaseService, register_services
from db.repositories.events_repo import EventsRepo
from models.pydantic_response_request_models.event_dto import (
    EventCreate,
    EventUpdate,
    EventRead,
    EventWithDetails,
    EventFilters,
    EventListResponse,
    EventStatus
)


@register_services("events")
class EventService(BaseService):
    
    async def get_event_by_id(self, event_id: int) -> EventWithDetails:
        """Получает детальную информацию о мероприятии"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            return event
    
    async def create_event(self, event_data: EventCreate, organizer_id: int) -> EventRead:
        """Создаёт новое мероприятие (только организатор)"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            new_event = await events_repo.create_event(event_data, organizer_id)
            await self.uow.commit()
            return new_event
    
    async def update_event(self, event_id: int, event_data: EventUpdate, user_id: int) -> EventRead:
        """Обновляет мероприятие (только организатор этого мероприятия)"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            
            # Проверяем, что мероприятие существует и пользователь - его организатор
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            
            if event.organizer_id != user_id:
                raise PermissionDeniedError("Вы не можете редактировать чужое мероприятие")
            
            updated_event = await events_repo.update_event(event_id, event_data)
            await self.uow.commit()
            return updated_event
    
    async def delete_event(self, event_id: int, user_id: int) -> dict:
        """Удаляет мероприятие (только организатор)"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            
            if event.organizer_id != user_id:
                raise PermissionDeniedError("Вы не можете удалить чужое мероприятие")
            
            deleted_count = await events_repo.delete_event(event_id)
            await self.uow.commit()
            
            return {"message": "Мероприятие успешно удалено", "deleted": deleted_count > 0}
    
    async def get_events_list(self, filters: EventFilters) -> EventListResponse:
        """Получает список мероприятий с фильтрацией и пагинацией"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            events_list = await events_repo.get_paginated_events(filters)
            return events_list
    
    async def get_my_events(self, organizer_id: int) -> list[EventRead]:
        """Получает все мероприятия организатора"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            my_events = await events_repo.get_events_by_organizer(organizer_id)
            return my_events
    
    async def update_event_status(self, event_id: int, status: EventStatus, user_id: int, is_admin: bool = False) -> dict:
        """
        Обновляет статус мероприятия.
        Организатор может отменить своё мероприятие (canceled).
        Админ может одобрить/отклонить (approved/pending).
        """
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            
            # Проверка прав
            if status == EventStatus.CANCELED:
                # Отменить может только организатор
                if event.organizer_id != user_id:
                    raise PermissionDeniedError("Только организатор может отменить мероприятие")
            elif status in [EventStatus.APPROVED, EventStatus.PENDING]:
                # Одобрить/отклонить может только админ
                if not is_admin:
                    raise PermissionDeniedError("Только администратор может изменять статус одобрения")
            else:
                raise BadRequestError(f"Недопустимый статус: {status}")
            
            success = await events_repo.update_event_status(event_id, status)
            await self.uow.commit()
            
            return {"message": f"Статус мероприятия изменён на {status}", "success": success}
