from fastapi import APIRouter, Depends, Response, status
from app.endpoints.authorization_methods.auth_user import verify_access_token_dependency
from app.endpoints.authorization_methods.email_send import verify_email_token_dependency
from app.services.services_factory import Services, get_services
from app.services.user_service import UserService
from models.pydantic_response_request_models.user_dto import UserCabinetInfo, UserUpdate, UserTokenInfo
from settings import settings

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserCabinetInfo)
async def get_my_profile(
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    user_service: UserService = services.users
    return await user_service.get_user_cabinet_info(user.user_id)

@router.patch("/me")
async def update_my_profile(
    update_data: UserUpdate,
    response: Response,
    user: UserTokenInfo = Depends(verify_access_token_dependency),
    services: Services = Depends(get_services)
):
    # Убедимся, что ID в update_data совпадает с токеном (или игнорируем ID из body)
    update_data.id = user.user_id
    
    user_service: UserService = services.users
    result = await user_service.update_user_profile(user.user_id, update_data)
    
    if result.get("email_verification_required"):
        # Если email изменился и пользователь деактивирован, нужно удалить куку доступа
        response.delete_cookie(settings.ACCESS_TOKEN_NAME)
        return {
            "message": result["message"],
            "user": result["user"],
            "status": "verification_required"
        }
    
    return result["user"]

@router.post("/reactivate")
async def reactivate_user(
    email: str = Depends(verify_email_token_dependency),
    services: Services = Depends(get_services)
):
    user_service: UserService = services.users
    await user_service.reactivate_user(email)
    return {"message": "Аккаунт успешно активирован. Теперь вы можете войти."}
