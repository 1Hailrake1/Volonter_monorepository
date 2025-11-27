from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from typing import Optional, AsyncGenerator
from settings import settings
from loguru import logger

class DBManager:

    def __init__(self):
        # общие настройки движка БД
        self.db_url = settings.FAST_API_DATABASE_URI
        self.db_pool_size = settings.DB_POOL_SIZE
        self.db_max_overflow = settings.DB_MAX_OVERFLOW

        # движок БД
        self.engine:Optional[AsyncEngine] = None

        # фабрика сессий
        self.session_maker:Optional[async_sessionmaker[AsyncSession]] = None

    async def _create_and_init_engine(self):
        # создание и сохранение движка в переменную класса
        if self.engine is not None:
            logger.error("Попытка повторой инициализации движка")
            raise RuntimeError("Engine is already initialized")

        self.engine = create_async_engine(
            self.db_url,
            pool_size=self.db_pool_size,
            max_overflow=self.db_max_overflow,
            pool_pre_ping=True,
            echo=False,
            pool_recycle=3600,
        )
        logger.info("Движок успешно создан")

    async def _create_and_init_session_maker(self):
        if self.session_maker is not None:
            logger.error("Попытка повторного создания фабрики сессий")
            raise RuntimeError("Sessionmaker is already initialized")

        if self.engine is None:
            logger.error("Engine не инициализирован перед созданием sessionmaker")
            raise RuntimeError("Engine must be initialized first")

        # создание и инициализация фабрики сессий
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Фабрика сессий успешно создана")

    async def _close(self):
        if self.engine:
            logger.info("Закрытие соединения с БД")
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            logger.info("Соединение с БД успешно разорвано")
        else:
            logger.error("Попытка закрыть неинициализированное соединение")

    async def health_check(self):
        try:
            async with self.get_session() as session:
                # Простой SELECT 1 для проверки соединения
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                logger.info("Соединение с БД стабильное")
                return True
        except Exception as e:
            logger.error(f"БД не отвечает: {e}")
            return False

    async def __aenter__(self):
        """
        Вход в контекстный менеджер - инициализация БД
        """
        logger.info("Инициализация DBManager")

        await self._create_and_init_engine()
        await self._create_and_init_session_maker()

        is_healthy = await self.health_check()
        if not is_healthy:
            logger.error("Database не прошла health check при инициализации")
            await self._close()
            raise RuntimeError("Database health check failed")

        logger.success("DBManager успешно инициализирован")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из контекстного менеджера - закрытие БД
        """
        if exc_type is not None:
            logger.error(f"Ошибка в контексте DBManager: {exc_type.__name__}: {exc_val}")

        await self._close()

        return False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:

        if self.session_maker is None:
            logger.error("Попытка получения сессии при неинициализированной, фабрике сессий")
            raise RuntimeError("session_maker not is initialized")

        async with self.session_maker() as session:
            try:
                yield session
            finally:
                logger.info("Закрываем сессию возвращая её в пул")
                await session.close()

db_manager = DBManager()

