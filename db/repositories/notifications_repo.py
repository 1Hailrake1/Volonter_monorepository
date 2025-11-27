from sqlalchemy import select, delete, update, func, insert
from typing import List

from models.orm_db_models.tables import Notifications
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.notification_dto import (
    NotificationRead,
    NotificationCreate,
    NotificationListResponse,
    NotificationFilters
)


@register_repository("notifications")
class NotificationsRepo(BaseRepo):

    async def create_notification(self, notif_in: NotificationCreate) -> NotificationRead:
        """Создает уведомление."""
        notif_orm = Notifications(**notif_in.model_dump())
        self.session.add(notif_orm)
        await self.session.flush()
        return NotificationRead.from_orm(notif_orm)

    async def bulk_create_notifications(self, notifs_in: List[NotificationCreate]) -> int:
        """Массовое создание уведомлений."""
        if not notifs_in:
            return 0
            
        values = [n.model_dump() for n in notifs_in]
        stmt = insert(Notifications).values(values)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_my_notifications(self, user_id: int, filters: NotificationFilters) -> NotificationListResponse:
        """Получает уведомления пользователя."""
        query = select(Notifications).where(Notifications.user_id == user_id)
        
        if filters.is_read is not None:
            query = query.where(Notifications.is_read == filters.is_read)
        if filters.type:
            query = query.where(Notifications.type == filters.type)
            
        # Order by created_at desc
        query = query.order_by(Notifications.created_at.desc())

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_stmt) or 0
        
        # Count unread (global for user)
        unread_stmt = select(func.count()).where(Notifications.user_id == user_id, Notifications.is_read == False)
        unread_count = await self.session.scalar(unread_stmt) or 0

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.limit(filters.page_size).offset(offset)

        result = await self.session.execute(query)
        notifs_orm = result.scalars().all()

        return NotificationListResponse(
            notifications=[NotificationRead.from_orm(n) for n in notifs_orm],
            total=total,
            unread_count=unread_count,
            page=filters.page,
            page_size=filters.page_size
        )

    async def mark_as_read(self, notification_ids: List[int], user_id: int) -> int:
        """Помечает уведомления как прочитанные."""
        stmt = (
            update(Notifications)
            .where(Notifications.id.in_(notification_ids), Notifications.user_id == user_id)
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def mark_all_as_read(self, user_id: int) -> int:
        """Помечает все уведомления пользователя как прочитанные."""
        stmt = (
            update(Notifications)
            .where(Notifications.user_id == user_id, Notifications.is_read == False)
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def delete_notification(self, notification_ids: List[int], user_id: int) -> int:
        """Удаляет уведомления."""
        stmt = (
            delete(Notifications)
            .where(Notifications.id.in_(notification_ids), Notifications.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.rowcount
