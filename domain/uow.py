from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SQLAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> SQLAlchemyUnitOfWork:
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session is None:
            return

        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()
    
    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise ValueError("Session is not initialized")
        
        return self._session

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
