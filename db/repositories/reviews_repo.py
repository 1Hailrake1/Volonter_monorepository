from sqlalchemy import select, func
from typing import List, Optional

from models.orm_db_models.tables import Reviews, Users, Events
from db.repositories.base_repo import BaseRepo
from db.unit_of_work import register_repository
from models.pydantic_response_request_models.review_dto import (
    ReviewRead,
    ReviewCreate,
    ReviewListResponse,
    ReviewWithUsers,
    ReviewFilters,
    UserReviewStats
)
from models.pydantic_response_request_models.user_dto import UserListItem


@register_repository("reviews")
class ReviewsRepo(BaseRepo):

    async def create_review(self, review_in: ReviewCreate, from_user_id: int) -> ReviewRead:
        """Создает новый отзыв."""
        review_orm = Reviews(**review_in.model_dump(), from_user_id=from_user_id)
        self.session.add(review_orm)
        await self.session.flush()
        return ReviewRead.from_orm(review_orm)

    async def get_review_by_id(self, review_id: int) -> ReviewRead | None:
        """Получает отзыв по ID."""
        review = await self.session.get(Reviews, review_id)
        return ReviewRead.from_orm(review) if review else None

    async def get_paginated_reviews(self, filters: ReviewFilters) -> ReviewListResponse:
        """Пагинированный список отзывов."""
        query = select(Reviews)

        if filters.event_id:
            query = query.where(Reviews.event_id == filters.event_id)
        if filters.from_user_id:
            query = query.where(Reviews.from_user_id == filters.from_user_id)
        if filters.to_user_id:
            query = query.where(Reviews.to_user_id == filters.to_user_id)
        if filters.min_rating:
            query = query.where(Reviews.rating >= filters.min_rating)

        count_stmt = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_stmt) or 0

        avg_stmt = select(func.avg(Reviews.rating)).select_from(query.subquery())
        average_rating = await self.session.scalar(avg_stmt)

        offset = (filters.page - 1) * filters.page_size
        query = query.limit(filters.page_size).offset(offset)

        result = await self.session.execute(query)
        reviews_orm = result.scalars().all()

        reviews_list = []
        for review in reviews_orm:
            from_user = await self.session.get(Users, review.from_user_id)
            to_user = await self.session.get(Users, review.to_user_id)
            
            reviews_list.append(ReviewWithUsers(
                **review.__dict__,
                from_user=UserListItem.from_orm(from_user),
                to_user=UserListItem.from_orm(to_user)
            ))

        return ReviewListResponse(
            reviews=reviews_list,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            average_rating=average_rating
        )

    async def get_user_rating_stats(self, user_id: int) -> UserReviewStats:
        """Получает статистику отзывов пользователя."""
        # Total reviews
        total_stmt = select(func.count()).where(Reviews.to_user_id == user_id)
        total = await self.session.scalar(total_stmt) or 0
        
        # Average rating
        avg_stmt = select(func.avg(Reviews.rating)).where(Reviews.to_user_id == user_id)
        avg = await self.session.scalar(avg_stmt) or 0.0

        dist_stmt = (
            select(Reviews.rating, func.count(Reviews.rating))
            .where(Reviews.to_user_id == user_id)
            .group_by(Reviews.rating)
        )
        dist_result = await self.session.execute(dist_stmt)
        distribution = {r: c for r, c in dist_result.all()}

        full_distribution = {i: distribution.get(i, 0) for i in range(1, 6)}

        return UserReviewStats(
            user_id=user_id,
            total_reviews=total,
            average_rating=avg,
            rating_distribution=full_distribution
        )
