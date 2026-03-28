"""Simple per-user rate limiting middleware."""

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

# Max messages per user per minute
RATE_LIMIT = 20
WINDOW = 60  # seconds

_user_timestamps: dict[int, list[float]] = {}


class ThrottleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        uid = event.from_user.id
        now = time.monotonic()

        timestamps = _user_timestamps.setdefault(uid, [])
        # Remove old timestamps outside the window
        timestamps[:] = [t for t in timestamps if now - t < WINDOW]

        if len(timestamps) >= RATE_LIMIT:
            return  # Silently drop

        timestamps.append(now)
        return await handler(event, data)
