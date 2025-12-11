from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.endpoints.authorization_methods.auth_user import verify_access_token_dependency
from app.services.services_factory import Services, get_services
from app.services.admin_service import AdminService
from app.services.user_service import UserService
from models.pydantic_response_request_models.role_dto import RoleRead
from models.pydantic_response_request_models.user_dto import UserTokenInfo, UserListResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin_role(user: UserTokenInfo = Depends(verify_access_token_dependency)) -> UserTokenInfo:
    """Проверяет, что пользователь имеет роль admin"""
    is_admin = any(role.role_name == "admin" for role in user.roles)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуется роль администратора."
        )
    return user


@router.get("/statistics")
async def get_platform_statistics(
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Получает общую статистику платформы (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.get_platform_statistics()


@router.get("/users", response_model=UserListResponse)
async def get_users_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Получает список всех пользователей (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.get_users_list(page, page_size)


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Блокирует пользователя (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.block_user(user_id)


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Разблокирует пользователя (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.unblock_user(user_id)


@router.post("/events/{event_id}/approve")
async def approve_event(
    event_id: int,
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Одобряет мероприятие (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.approve_event(event_id)


@router.post("/events/{event_id}/reject")
async def reject_event(
    event_id: int,
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Отклоняет мероприятие (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.reject_event(event_id)


@router.get("/events/pending")
async def get_pending_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Получает список мероприятий, ожидающих одобрения (только для админа)"""
    admin_service: AdminService = services.admin
    return await admin_service.get_pending_events(page, page_size)

@router.post("/users/{user_id}/change_roles")
async def change_roles(
        user_id:int,
        new_roles:list[RoleRead],
        user: UserTokenInfo = Depends(verify_admin_role),
        services: Services = Depends(get_services),
):
    admin_service: AdminService = services.admin
    return await admin_service.change_roles(user_id, new_roles)


@router.get("/roles")
async def get_all_roles(
    user: UserTokenInfo = Depends(verify_admin_role),
    services: Services = Depends(get_services)
):
    """Получает список всех доступных ролей"""
    admin_service: AdminService = services.admin
    return await admin_service.get_all_roles()
