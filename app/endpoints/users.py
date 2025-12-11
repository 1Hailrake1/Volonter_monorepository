from fastapi import APIRouter, Depends, Response, status
from app.endpoints.authorization_methods.auth_user import verify_access_token_dependency
from app.endpoints.authorization_methods.email_send import verify_email_token_dependency
from app.services.services_factory import Services, get_services
from app.services.user_service import UserService
from models.pydantic_response_request_models.role_dto import RoleRead, RoleListResponse
from models.pydantic_response_request_models.skill_dto import SkillRead, SkillListResponse
from models.pydantic_response_request_models.user_dto import UserCabinetInfo, UserUpdate, UserTokenInfo
from settings import settings

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/info", response_model=UserCabinetInfo)
async def get_user_profile_info(
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    user_service: UserService = services.users
    return await user_service.get_user_cabinet_info(user.user_id)

@router.put("/update", response_model=UserCabinetInfo)
async def update_user_cabinet_info(
        user_update: UserUpdate,
        user: UserCabinetInfo = Depends(verify_access_token_dependency),
        services: Services = Depends(get_services),
):
    user_service: UserService = services.users
    return await user_service.update_user(user_update)

@router.get("/roles", response_model=RoleListResponse)
async def get_user_roles(
        user_roles: UserCabinetInfo = Depends(verify_access_token_dependency),
        services: Services = Depends(get_services),
):
    user_service: UserService = services.users
    return await user_service.get_roles()

