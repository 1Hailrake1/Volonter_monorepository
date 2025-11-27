from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.endpoints.authorization_methods.auth_user import verify_access_token_dependency
from app.services.services_factory import Services, get_services
from app.services.application_service import ApplicationService
from models.pydantic_response_request_models.user_dto import UserTokenInfo
from models.pydantic_response_request_models.application_dto import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusUpdate,
    ApplicationListResponse,
    ApplicationStatus,
    ApplicationBulkApprove,
    ApplicationBulkReject
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationRead)
async def create_application(
    app_data: ApplicationCreate,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Создаёт заявку на участие в мероприятии"""
    application_service: ApplicationService = services.applications
    return await application_service.create_application(app_data, user.user_id)


@router.get("/{app_id}", response_model=ApplicationRead)
async def get_application(
    app_id: int,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Получает заявку по ID"""
    application_service: ApplicationService = services.applications
    return await application_service.get_application_by_id(app_id)


@router.patch("/{app_id}/status")
async def update_application_status(
    app_id: int,
    status_data: ApplicationStatusUpdate,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """
    Обновляет статус заявки.
    Организатор может одобрить/отклонить.
    Волонтёр может отменить свою заявку.
    """
    application_service: ApplicationService = services.applications
    return await application_service.update_application_status(
        app_id,
        status_data.status,
        user.user_id
    )


@router.get("/my/list", response_model=ApplicationListResponse)
async def get_my_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Получает все заявки текущего пользователя (волонтёра)"""
    application_service: ApplicationService = services.applications
    return await application_service.get_my_applications(user.user_id, page, page_size)


@router.get("/event/{event_id}", response_model=ApplicationListResponse)
async def get_event_applications(
    event_id: int,
    status: Optional[ApplicationStatus] = Query(None, description="Фильтр по статусу"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Получает все заявки на мероприятие (только для организатора)"""
    application_service: ApplicationService = services.applications
    return await application_service.get_event_applications(
        event_id,
        user.user_id,
        status,
        page,
        page_size
    )


@router.post("/bulk/approve")
async def bulk_approve_applications(
    data: ApplicationBulkApprove,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Массовое одобрение заявок (только организатор)"""
    application_service: ApplicationService = services.applications
    return await application_service.bulk_approve_applications(data, user.user_id)


@router.post("/bulk/reject")
async def bulk_reject_applications(
    data: ApplicationBulkReject,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    """Массовое отклонение заявок (только организатор)"""
    application_service: ApplicationService = services.applications
    return await application_service.bulk_reject_applications(data, user.user_id)
