from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from app.services.services_factory import Services, get_services
from app.services.public_service import PublicService
from models.pydantic_response_request_models.user_dto import UserPublic
from models.pydantic_response_request_models.event_dto import EventListResponse
from models.pydantic_response_request_models.tag_dto import TagRead
from models.pydantic_response_request_models.skill_dto import SkillRead

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/events", response_model=EventListResponse)
async def get_public_events(
    location: Optional[str] = Query(None, description="Фильтр по городу"),
    tag_ids: Optional[str] = Query(None, description="ID тегов через запятую"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    services: Services = Depends(get_services)
):
    """
    Получает список одобренных мероприятий для публичной страницы.
    НЕ требует авторизации.
    """
    public_service: PublicService = services.public
    
    # Парсим tag_ids если они переданы
    tag_ids_list = [int(x) for x in tag_ids.split(",")] if tag_ids else None
    
    return await public_service.get_public_events(
        location=location,
        tag_ids=tag_ids_list,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}", response_model=UserPublic)
async def get_public_user_profile(
    user_id: int,
    services: Services = Depends(get_services)
):
    """
    Получает публичный профиль пользователя.
    НЕ требует авторизации.
    """
    public_service: PublicService = services.public
    return await public_service.get_public_user_profile(user_id)


@router.get("/tags", response_model=List[TagRead])
async def get_all_tags(services: Services = Depends(get_services)):
    """
    Получает список всех тегов.
    НЕ требует авторизации.
    """
    public_service: PublicService = services.public
    return await public_service.get_all_tags()


@router.get("/skills", response_model=List[SkillRead])
async def get_all_skills(services: Services = Depends(get_services)):
    """
    Получает список всех навыков.
    НЕ требует авторизации.
    """
    public_service: PublicService = services.public
    return await public_service.get_all_skills()
