from app.core.exceptions import NotFoundError
from app.services.services_factory import BaseService, register_services
from db.repositories.user_repo import UserRepo
from db.repositories.events_repo import EventsRepo
from db.repositories.tags_repo import TagsRepo
from db.repositories.skills_repo import SkillsRepo
from models.pydantic_response_request_models.user_dto import UserPublic
from models.pydantic_response_request_models.event_dto import EventFilters, EventListResponse, EventStatus
from models.pydantic_response_request_models.tag_dto import TagRead
from models.pydantic_response_request_models.skill_dto import SkillRead, SkillListResponse
from typing import List


@register_services("public")
class PublicService(BaseService):
    
    async def get_public_events(
        self,
        location: str = None,
        tag_ids: list[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> EventListResponse:
        """
        Получает список одобренных мероприятий для публичной страницы.
        Показываются только мероприятия со статусом 'approved'.
        """
        async with self.uow:
            events_repo: EventsRepo = self.uow.events
            
            filters = EventFilters(
                status=EventStatus.APPROVED,
                location=location,
                tag_ids=tag_ids,
                page=page,
                page_size=page_size
            )
            
            events = await events_repo.get_paginated_events(filters)
            return events
    
    async def get_public_user_profile(self, user_id: int) -> UserPublic:
        """Получает публичный профиль пользователя"""
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            
            user = await user_repo.get_user_public_profile(user_id)
            if not user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            return user
    
    async def get_all_tags(self) -> List[TagRead]:
        """Получает список всех тегов"""
        async with self.uow:
            tags_repo: TagsRepo = self.uow.tags
            return await tags_repo.get_all_tags()
    
    async def get_all_skills(self) -> SkillListResponse:
        """Получает список всех навыков"""
        async with self.uow:
            skills_repo: SkillsRepo = self.uow.skills
            return await skills_repo.get_all_skills()
