from redis.asyncio import Redis
from typing import List

from .base import BaseCache
from domain.cache import keys
from domain.objects import entities


class ModerationCache(BaseCache):

    def __init__(self, redis: Redis, tracker_ttl: int = 60 * 60):
        super().__init__(redis)
        self.tracker_ttl = tracker_ttl

    async def get_trackers(
        self, user_id: int
    ) -> List[entities.TrackerWithUserEntity] | None:
        trackers = await self.get(keys.get_trackers_key(user_id))

        if trackers:
            return [
                entities.TrackerWithUserEntity.model_validate_json(tracker)
                for tracker in trackers
            ]

        return None

    async def set_trackers(
        self, user_id: int, trackers: List[entities.TrackerWithUserEntity]
    ) -> None:
        await self.set(
            keys.get_trackers_key(user_id),
            [tracker.model_dump() for tracker in trackers],
            expire=self.tracker_ttl,
        )

    async def set_tracker_message(self, tracker_id: int, message_id: int) -> None:
        await self.set(
            keys.get_tracker_message_key(tracker_id),
            message_id,
            expire=self.tracker_ttl,
        )

    async def get_tracker_message(self, tracker_id: int) -> int | None:
        return await self.get(keys.get_tracker_message_key(tracker_id))

    async def invalidate_trackers(self, user_id: int) -> None:
        await self.delete(keys.get_trackers_key(user_id))
