import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.core.exceptions import UnauthorizedError
from app.endpoints.authorization_methods.email_send import verify_email_token_dependency
from app.security.generate_jwt_keys import decode_jwt_token
from app.services.auth_service import AuthService
from app.services.services_factory import Services, get_services
from models.pydantic_response_request_models.user_dto import UserLogin, UserRegister, UserTokenInfo
from settings import settings

router = APIRouter(prefix="/login")

@router.post("/")
async def login(
        response:Response,
        user_login: UserLogin,
        email: str = Depends(verify_email_token_dependency),
        services:Services = Depends(get_services),
):
    auth_service:AuthService = services.auth
    token = await auth_service.login(user_login)
    max_age = int(settings.ACCESS_TOKEN_EXPIRE)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_NAME,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
        expires=max_age,
        path="/",
    )
    return {
        "status": "success",
        "token": token,
    }

@router.post("/register")
async def register(
        user_register: UserRegister,
        email: str = Depends(verify_email_token_dependency),
        services:Services = Depends(get_services),
):
    auth_service:AuthService = services.auth
    new_user = await auth_service.register(user_register)

    return {
        "status": "success",
        "new_user": new_user,
    }


async def verify_access_token_dependency(request: Request) -> UserTokenInfo:
    """
    Извлекает токен верификации из Cookie (ACCESS_TOKEN_NAME),
    декодирует его, проверяет тип ('access_token') и срок годности.

    Возвращает UserTokenInfo пользователя, если токен валиден.

    Используется для защиты конечных точек, требующих подтверждения логина
    """
    access_token = request.cookies.get(settings.ACCESS_TOKEN_NAME)
    if not access_token:
        raise UnauthorizedError("Необходим токен доступа. Пройдите аутентификацию.")

    try:
        payload = decode_jwt_token(access_token)

        if payload.get("type") != settings.ACCESS_TOKEN_NAME:
            raise UnauthorizedError("Неверный тип токена. Ожидается 'access_token'.")

        user_token_info = UserTokenInfo(
            user_id=payload.get("user_id"),
            email=payload.get("email"),
            roles=payload.get("roles"),
        )

        return user_token_info

    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Токен верификации истёк. Начните процесс заново.")


@router.post("/me")
async def get_me(
        request: Request,
        user:UserTokenInfo = Depends(verify_access_token_dependency)
):
    return user