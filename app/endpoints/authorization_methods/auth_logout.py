from fastapi import APIRouter, Response, status
from settings import settings

router = APIRouter(prefix="/logout", tags=["auth"])

@router.post("/", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_NAME,
        path="/",
        httponly=True,
        samesite="lax"
    )
    return {"message": "Вы успешно вышли из системы"}
