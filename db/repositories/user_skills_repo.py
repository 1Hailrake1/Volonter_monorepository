from sqlalchemy import delete, insert
from db.unit_of_work import register_repository
from db.repositories.base_repo import BaseRepo
from models.orm_db_models.tables import UserSkills
from models.pydantic_response_request_models.skill_dto import SkillRead


@register_repository("user_skills")
class UserSkillsRepo(BaseRepo):

    async def update_user_skills(self, user_id:int, skills:list[SkillRead]):
        delete_all_skills = delete(UserSkills).where(UserSkills.user_id == user_id)
        await self.session.execute(delete_all_skills)

        if not skills:
            return []

        new_skills = [
            {"user_id":user_id, "skill_id":skill.id}
            for skill in skills
        ]

        result = await self.session.execute(
            insert(UserSkills), new_skills
        )

        return new_skills

