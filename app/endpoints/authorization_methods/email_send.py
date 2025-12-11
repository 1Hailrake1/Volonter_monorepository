import jwt
from fastapi import Depends, FastAPI, HTTPException, APIRouter, status, Response, Request
from app.email_functools.email_sender import EmailSender
from app.email_functools.verify_codes_storage import codes_storage
from app.core.exceptions import UnauthorizedError, InternalServerError
from models.pydantic_response_request_models.email_dto import SendCodeRequest, VerifyCodeResponse, VerifyCodeRequest
from app.security.generate_jwt_keys import create_jwt_token, decode_jwt_token
from settings import settings

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send-code", status_code=status.HTTP_200_OK)
async def send_verify_code(
        data: SendCodeRequest,
):
    email_sender = EmailSender()
    code = codes_storage.put_code(data.email)
    try:
        await email_sender.send_verification_code(data.email, code)
    except Exception as e:
        raise InternalServerError(f"Не удалось отправить email: {e}")

    return {
        "message": f"Код отправлен на {data.email}",
        "expires_in_minutes": settings.VERIFY_CODE_EXPIRE
    }


@router.post("/verify_code", response_model=VerifyCodeResponse)
async def verify_code(
        data: VerifyCodeRequest,
        response:Response
):
    print(data, data.email, data.code)
    print(codes_storage, codes_storage._codes)
    if not codes_storage.verify_code(data.email, data.code):
        raise UnauthorizedError("Неверный или истекший код верификации")

    claims = {"email": data.email}
    verification_token = create_jwt_token(
        claims=claims,
        type=settings.VERIFY_TOKEN_NAME,

    )

    max_age = int(settings.VERIFY_TOKEN_EXPIRE)
    response.set_cookie(
        key=settings.VERIFY_TOKEN_NAME,
        value=verification_token,
        httponly=True,
        secure=False,  # в проде True; локально можно False
        samesite="lax",
        max_age=max_age,
        expires=max_age,
        path="/",
    )

    return VerifyCodeResponse(
        message="Email подтвержден",
        verification_token=verification_token,
        expires_in_seconds=settings.VERIFY_TOKEN_EXPIRE,
    )


async def verify_email_token_dependency(request: Request):
    """
    Извлекает токен верификации из Cookie (VERIFY_TOKEN_NAME),
    декодирует его, проверяет тип ('verify_token') и срок годности.

    Возвращает email пользователя, если токен валиден.

    Используется для защиты конечных точек, требующих подтверждения email,
    например, установки пароля после верификации.
    """
    verification_token = request.cookies.get(settings.VERIFY_TOKEN_NAME)

    if not verification_token:
        raise UnauthorizedError("Необходим токен верификации email. Пройдите верификацию.")

    try:
        payload = decode_jwt_token(verification_token)

        if payload.get("type") != settings.VERIFY_TOKEN_NAME:
            raise UnauthorizedError("Неверный тип токена. Ожидается 'verify_token'.")

        email = payload.get("email")
        if not email:
            raise UnauthorizedError("Токен не содержит email пользователя.")

        return email

    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Токен верификации истёк. Начните процесс заново.")

