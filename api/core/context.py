from contextvars import ContextVar
from typing import Optional

from domain.uow import SQLAlchemyUnitOfWork


_uow_context: ContextVar[Optional[SQLAlchemyUnitOfWork]] = ContextVar("uow", default=None)


class UOWContextManager:

    @staticmethod
    def get_current_uow() -> SQLAlchemyUnitOfWork:
        uow = _uow_context.get()

        if uow is None:
            raise RuntimeError(
                "UnitOfWork is not set in current context. "
                "Make sure you're using @with_uow decorator or uow_context manager."
            )

        return uow


    @staticmethod
    def set_current_uow(uow: SQLAlchemyUnitOfWork) -> None:
        _uow_context.set(uow)


    @staticmethod
    def clear_current_uow() -> None:
        _uow_context.set(None)


class UOWContext:

    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self.uow = uow
        self._token = None

    async def __aenter__(self):
        self._token = _uow_context.set(self.uow)
        await self.uow.__aenter__()
        return self.uow

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            return await self.uow.__aexit__(exc_type, exc_val, exc_tb)
        finally:
            _uow_context.reset(self._token)
