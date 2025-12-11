from app.core.exceptions import NotFoundError, AlreadyExistsError, InternalServerError
from app.services.services_factory import BaseService, register_services
from db.repositories.roles_repo import RolesRepo
from db.repositories.skills_repo import SkillsRepo
from db.repositories.user_repo import UserRepo
from db.repositories.user_skills_repo import UserSkillsRepo
from models.pydantic_response_request_models.role_dto import RoleRead, RoleListResponse
from models.pydantic_response_request_models.skill_dto import SkillRead, SkillListResponse
from models.pydantic_response_request_models.user_dto import UserCabinetInfo, UserUpdate
from app.email_functools.email_sender import EmailSender
from app.email_functools.verify_codes_storage import codes_storage
from settings import settings

@register_services("users")
class UserService(BaseService):
    
    async def get_user_cabinet_info(self, user_id: int) -> UserCabinetInfo:
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            user_info = await user_repo.get_user_cabinet_info(user_id)
            if not user_info:
                raise NotFoundError("Пользователь не найден")
            return user_info

    async def update_user(self, user_update: UserUpdate) -> UserCabinetInfo:
        async with self.uow:
            user_repo: UserRepo = self.uow.users
            user_skills_repo: UserSkillsRepo = self.uow.user_skills
            roles_repo: RolesRepo = self.uow.roles

            await user_repo.update_user(user_update)
            await user_skills_repo.update_user_skills(user_update.id, user_update.skills)
            for role in user_update.roles:
                await roles_repo.add_role_to_user(user_update.id, role.id)

            new_user_info = await user_repo.get_user_cabinet_info(user_update.id)
            await self.uow.commit()
        return new_user_info

    async def get_roles(self) -> RoleListResponse:
        async with self.uow:
            roles_repo: RolesRepo = self.uow.roles

            result = await roles_repo.get_all_roles()
        return result

    async def get_skills(self) -> SkillListResponse:
        async with self.uow:
            skills_repo: SkillsRepo = self.uow.skills

            result = await skills_repo.get_all_skills()
        return result