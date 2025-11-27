from fastapi import APIRouter
from .authorization_methods import router as auth_router
from .users import router as users_router
from .events import router as events_router
from .applications import router as applications_router
from .admin import router as admin_router
from .public import router as public_router


main_router = APIRouter(prefix="/v1")
main_router.include_router(auth_router)
main_router.include_router(users_router)
main_router.include_router(events_router)
main_router.include_router(applications_router)
main_router.include_router(admin_router)
main_router.include_router(public_router)

__all__ = ["main_router"]