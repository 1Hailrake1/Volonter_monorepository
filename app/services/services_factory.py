from abc import ABC
from typing import Dict, Type
from fastapi import Depends
from loguru import logger
from db.unit_of_work import UnitOfWork, get_uow


class BaseService(ABC):
    def __init__(self, uow:UnitOfWork):
        self.uow = uow


class Services:
    def __init__(self, uow:UnitOfWork, services_registry:Dict[str, Type[BaseService]]):
        self._uow = uow
        self._services_registry:Dict[str, Type[BaseService]] = services_registry
        self._services:Dict[str, BaseService] = {}

    def _initialize_services(self):
        if not self._services:
            for name, service in self._services_registry.items():
                self._services[name] = service(self._uow)
                logger.info(f"Инициализирован сервис: {name}, класс: {service}")

    def __getattr__(self, name:str):
        self._initialize_services()

        if name in self._services:
            return self._services[name]

        logger.error(f"Сервис {name} не найден в реестре Сервисов")
        raise AttributeError(f"Service {name} has found in registry")


SERVICES_REGISTRY = {}

def register_services(name:str):
    def decorator(cls:Type[BaseService]):
        SERVICES_REGISTRY[name] = cls
        return cls
    return decorator

async def get_services(
        uow:UnitOfWork = Depends(get_uow),
)-> Services:
    return Services(uow, SERVICES_REGISTRY)
