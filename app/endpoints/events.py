from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.endpoints.authorization_methods.auth_user import verify_access_token_dependency
from app.services.services_factory import Services, get_services
from app.services.event_service import EventService
from models.pydantic_response_request_models.user_dto import UserTokenInfo
from models.pydantic_response_request_models.event_dto import (
    EventCreate,
    EventUpdate,
    EventWithDetails,
    EventRead,
    EventFilters,
    EventListResponse,
    EventStatusUpdate
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=EventListResponse)
async def get_events_list(
    location: Optional[str] = Query(None, description="Фильтр по городу"),
    tag_ids: Optional[str] = Query(None, description="ID тегов через запятую"),
    status: Optional[str] = Query(None, description="Статус мероприятия"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Получает список мероприятий с фильтрацией"""
    event_service: EventService = services.events
    
    # Парсим tag_ids если они переданы
    tag_ids_list = [int(x) for x in tag_ids.split(",")] if tag_ids else None
    
    filters = EventFilters(
        location=location,
        tag_ids=tag_ids_list,
        status=status,
        page=page,
        page_size=page_size
    )
    
    return await event_service.get_events_list(filters)


@router.get("/{event_id}", response_model=EventWithDetails)
async def get_event_details(
    event_id: int,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Получает детальную информацию о мероприятии"""
    event_service: EventService = services.events
    return await event_service.get_event_by_id(event_id)


@router.post("/", response_model=EventRead)
async def create_event(
    event_data: EventCreate,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Создаёт новое мероприятие (только для организаторов)"""
    event_service: EventService = services.events
    return await event_service.create_event(event_data, user.user_id)


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Обновляет мероприятие (только организатор)"""
    event_service: EventService = services.events
    return await event_service.update_event(event_id, event_data, user.user_id)


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Удаляет мероприятие (только организатор)"""
    event_service: EventService = services.events
    return await event_service.delete_event(event_id, user.user_id)


@router.get("/my/organized", response_model=list[EventRead])
async def get_my_events(
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Получает все мероприятия текущего пользователя"""
    event_service: EventService = services.events
    return await event_service.get_my_events(user.user_id)


@router.patch("/{event_id}/status")
async def update_event_status(
    event_id: int,
    status_data: EventStatusUpdate,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """
    Обновляет статус мероприятия.
    Организатор может отменить (canceled).
    Админ может одобрить/отклонить (approved/pending).
    """
    event_service: EventService = services.events
    
    # Проверяем, является ли пользователь админом
    is_admin = any(role.role_name == "admin" for role in user.roles)
    
    return await event_service.update_event_status(
        event_id, 
        status_data.status, 
        user.user_id,
        is_admin
    )
