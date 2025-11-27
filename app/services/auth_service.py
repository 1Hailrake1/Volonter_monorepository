from app.core.exceptions import AlreadyExistsError, UnauthorizedError, PermissionDeniedError
from app.security.generate_jwt_keys import create_jwt_token
from app.security.passwords import verify_password, hash_pwd
from app.services.services_factory import BaseService, register_services
from db.repositories.roles_repo import RolesRepo
from db.repositories.user_repo import UserRepo
from models.pydantic_response_request_models.user_dto import UserRegister, UserLogin, UserRead


@register_services("auth")
class AuthService(BaseService):

    async def login(self, credentials: UserLogin) -> str:

        async with self.uow:
            user_repo:UserRepo = self.uow.users
            roles_repo:RolesRepo = self.uow.roles
            user = await user_repo.get_user_by_email(credentials.email)
            if user:
                roles = await roles_repo.get_user_roles(user.id)

            await self.uow.commit()

        if user is None:
            raise UnauthorizedError("Неверный email или пароль")

        if not user.is_active:
            raise PermissionDeniedError(f"У пользователя с email - {credentials.email} нет доступа")

        if not verify_password(credentials.hashed_password, user.hashed_password):
            raise UnauthorizedError("Неверный email или пароль")

        return create_jwt_token(
            claims={
                "user_id":str(user.id),
                "email":str(user.email),
                "roles":[role.model_dump() for role in roles]
            },
        )

    async def register(self, user:UserRegister) -> UserRead:
        async with self.uow:
            user_repo:UserRepo = self.uow.users

            if await user_repo.exists_user(user.email):
               raise AlreadyExistsError("Пользователь с таким email уже существует")

            user.hashed_password = hash_pwd(user.hashed_password)

            new_user = await user_repo.create_user(user)
            await self.uow.commit()

        return new_user