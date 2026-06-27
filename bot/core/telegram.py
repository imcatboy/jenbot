import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_telegram_retry(
    factory: Callable[[], Awaitable[T]], *, max_retries: int = 5
) -> T:
    for attempt in range(max_retries):
        try:
            return await factory()
        except TelegramRetryAfter as e:
            if attempt == max_retries - 1:
                raise

            wait = e.retry_after + 1
            logger.warning(
                "Telegram flood control on %s, retry in %s s (%s/%s)",
                e.method.__class__.__name__,
                wait,
                attempt + 1,
                max_retries,
            )
            await asyncio.sleep(wait)
        except TelegramNetworkError:
            if attempt == max_retries - 1:
                raise

            wait = 2**attempt
            logger.warning(
                "Telegram network error, retry in %s s (%s/%s)",
                wait,
                attempt + 1,
                max_retries,
            )
            await asyncio.sleep(wait)

    raise RuntimeError("unreachable")
