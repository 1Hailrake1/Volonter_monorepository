from fastapi import APIRouter
from .email_send import router as email_router
from .auth_user import router as auth_user_router
from .auth_logout import router as auth_logout_router

router = APIRouter(prefix='/auth')

router.include_router(email_router)
router.include_router(auth_user_router)
router.include_router(auth_logout_router)