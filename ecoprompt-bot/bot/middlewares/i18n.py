import json
from pathlib import Path
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.db.crud import get_or_create_user
from bot.db.session import async_session

LOCALES_DIR = Path(__file__).parent.parent / "i18n"
_translations: dict[str, dict[str, str]] = {}


def load_translations() -> None:
    for lang_file in LOCALES_DIR.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, encoding="utf-8") as f:
            _translations[lang] = json.load(f)


def t(key: str, lang: str = "ru", **kwargs: Any) -> str:
    text = _translations.get(lang, {}).get(key)
    if text is None:
        text = _translations.get("ru", {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        telegram_user = None
        if isinstance(event, Message) and event.from_user:
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            telegram_user = event.from_user

        if telegram_user:
            async with async_session() as session:
                user = await get_or_create_user(
                    session, telegram_user.id, telegram_user.username
                )
                data["db_user"] = user
                data["session"] = session
                data["lang"] = user.language
                data["t"] = lambda key, **kw: t(key, user.language, **kw)
                return await handler(event, data)

        data["lang"] = "ru"
        data["t"] = lambda key, **kw: t(key, "ru", **kw)
        return await handler(event, data)
