from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Type

from db.manager import db_manager
from db.repositories.base_repo import BaseRepo
from loguru import logger

class UnitOfWork:
    def __init__(self, db_session:AsyncSession, repo_registry:Dict[str, Type[BaseRepo]]):
        self.session = db_session
        self._repo_registry = repo_registry
        self._repositories:Dict[str, BaseRepo] = {}
        self._is_committed = False

    def _initialize_repositories(self):
        if not self._repositories:
            for repo_name, repo_cls in self._repo_registry.items():
                self._repositories[repo_name] = repo_cls(self.session)
                logger.info(f"Инициализирован репозиторий: {repo_name}, класс: {repo_cls}")

    async def commit(self):
        if self._is_committed:
            raise RuntimeError("Cannot commit - already committed")
        try:
            await self.session.commit()
            self._is_committed = True
            logger.info(f"Транзакция успешно зафиксирована (коммит выполнен). Статус: {self._is_committed}")
        except Exception as e:
            logger.error(f"Сбой фиксации (commit failed): {e}")
            raise e

    async def rollback(self):
        if self._is_committed:
            raise RuntimeError("Cannot rollback - transaction is already committed")

        await self.session.rollback()
        logger.warning(f"Откат транзакции (rollback transaction)")


    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            await self.rollback()
            logger.error(f"Сбой транзакции (Transaction failed): {exc_type.__name__}: {exc_val}")
        elif not self._is_committed:
            logger.warning("Транзакция завершена без явного коммита - выполняется откат (rolling back)")
            await self.rollback()

        return False

    def __getattr__(self, name:str):
        self._initialize_repositories()
        if name in self._repositories:
            return self._repositories[name]

        logger.error(f"Репозиторий {name} не найден в реестре UoW")
        raise AttributeError(f"Repository {name} has found in registry")

REPOSITORY_REGISTRY:Dict[str, Type[BaseRepo]] = {}

def register_repository(name:str):
    def decorator(repo_class: Type[BaseRepo]):
        REPOSITORY_REGISTRY[name] = repo_class
        return repo_class
    return decorator



async def get_uow(
        db_session_maker:AsyncSession = Depends(db_manager.get_session),
):
    async with db_session_maker as db_session:
        uow = UnitOfWork(db_session, REPOSITORY_REGISTRY)
        try:
            yield uow
        except Exception as e:
            await uow.rollback()
            logger.error(f"Ошибка обработки в транзакции {e}, выполняем roollback")
            raise
        finally:
            pass