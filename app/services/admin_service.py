from typing import List, Optional
from datetime import datetime
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.services.services_factory import BaseService, register_services
from db.repositories.roles_repo import RolesRepo
from db.repositories.user_repo import UserRepo
from db.repositories.events_repo import EventsRepo
from db.repositories.applications_repo import ApplicationsRepo
from models.pydantic_response_request_models.role_dto import RoleRead
from models.pydantic_response_request_models.user_dto import UserListResponse, UserCabinetInfo
from models.pydantic_response_request_models.event_dto import EventStatus, EventFilters
from models.pydantic_response_request_models.application_dto import ApplicationStatus


@register_services("admin")
class AdminService(BaseService):
    
    async def get_platform_statistics(self) -> dict:
        """Получает общую статистику платформы"""
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            events_repo: EventsRepo = self.uow.events
            
            # Общее количество пользователей
            total_users = await user_repo.get_total_users_count()
            
            # Статистика по мероприятиям
            all_events_filters = EventFilters(page=1, page_size=1)
            events_data = await events_repo.get_paginated_events(all_events_filters)
            total_events = events_data.total
            
            # Мероприятия по статусам
            pending_events_filters = EventFilters(status=EventStatus.PENDING, page=1, page_size=1)
            pending_events = await events_repo.get_paginated_events(pending_events_filters)
            
            approved_events_filters = EventFilters(status=EventStatus.APPROVED, page=1, page_size=1)
            approved_events = await events_repo.get_paginated_events(approved_events_filters)
            
            completed_events_filters = EventFilters(status=EventStatus.COMPLETED, page=1, page_size=1)
            completed_events = await events_repo.get_paginated_events(completed_events_filters)
            
            return {
                "total_users": total_users,
                "total_events": total_events,
                "events_by_status": {
                    "pending": pending_events.total,
                    "approved": approved_events.total,
                    "completed": completed_events.total
                },
                "generated_at": datetime.now()
            }
    
    async def get_users_list(self, page: int = 1, page_size: int = 20) -> UserListResponse:
        """Получает список всех пользователей (для админа)"""
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            users = await user_repo.get_paginated_users(page, page_size)
            return users
    
    async def block_user(self, user_id: int) -> dict:
        """Блокирует пользователя (is_active = False)"""
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            
            user = await user_repo.get_user(user_id)
            if not user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            if not user.is_active:
                return {"message": "Пользователь уже заблокирован", "already_blocked": True}
            
            success = await user_repo.set_user_active_status(user_id, False)
            await self.uow.commit()
            
            return {"message": "Пользователь успешно заблокирован", "success": success}
    
    async def unblock_user(self, user_id: int) -> dict:
        """Разблокирует пользователя (is_active = True)"""
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            
            user = await user_repo.get_user(user_id)
            if not user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            if user.is_active:
                return {"message": "Пользователь уже активен", "already_active": True}
            
            success = await user_repo.set_user_active_status(user_id, True)
            await self.uow.commit()
            
            return {"message": "Пользователь успешно разблокирован", "success": success}
    
    async def approve_event(self, event_id: int) -> dict:
        """Одобряет мероприятие (меняет статус на approved)"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            
            if event.status == EventStatus.APPROVED:
                return {"message": "Мероприятие уже одобрено", "already_approved": True}
            
            success = await events_repo.update_event_status(event_id, EventStatus.APPROVED)
            await self.uow.commit()
            
            return {"message": "Мероприятие успешно одобрено", "success": success}
    
    async def reject_event(self, event_id: int) -> dict:
        """Отклоняет мероприятие (меняет статус на pending или можно добавить rejected)"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            
            event = await events_repo.get_event_by_id(event_id)
            if not event:
                raise NotFoundError(f"Мероприятие с ID {event_id} не найдено")
            
            # Возвращаем в pending (или можно создать статус rejected)
            success = await events_repo.update_event_status(event_id, EventStatus.PENDING)
            await self.uow.commit()
            
            return {"message": "Мероприятие отклонено", "success": success}
    
    async def get_pending_events(self, page: int = 1, page_size: int = 20):
        """Получает список мероприятий, ожидающих одобрения"""
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            filters = EventFilters(status=EventStatus.PENDING, page=page, page_size=page_size)
            pending_events = await events_repo.get_paginated_events(filters)
            await self.uow.commit()
            return pending_events


    async def change_roles(self, user_id: int, new_roles: List[RoleRead]) -> UserCabinetInfo:
        async with self.uow:
            roles_repo: RolesRepo = self.uow.roles
            user_repo: UserRepo = self.uow.users
            
            # 1. Получаем текущие роли
            current_roles = await roles_repo.get_user_roles(user_id)
            current_role_ids = {r.id for r in current_roles}
            new_role_ids = {r.id for r in new_roles}

            # 2. Вычисляем разницу
            roles_to_add = new_role_ids - current_role_ids
            roles_to_remove = current_role_ids - new_role_ids

            # 3. Применяем изменения
            for role_id in roles_to_add:
                await roles_repo.add_role_to_user(user_id, role_id)
                
            for role_id in roles_to_remove:
                await roles_repo.remove_role_from_user(user_id, role_id)

            # 4. Возвращаем обновленного пользователя
            new_user = await user_repo.get_user_cabinet_info(user_id)
            await self.uow.commit()
            
        return new_user

    async def get_all_roles(self):
        async with self.uow:
            roles_repo: RolesRepo = self.uow.roles
            return await roles_repo.get_all_roles()
