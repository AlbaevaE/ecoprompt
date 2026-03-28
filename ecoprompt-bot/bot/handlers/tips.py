import json
from pathlib import Path

from aiogram import F, Router
from aiogram.types import Message

from bot.db import crud

router = Router()

TIPS_DIR = Path(__file__).parent.parent / "content" / "tips"
_tips: dict[str, list[str]] = {}


def load_tips() -> None:
    for lang_file in TIPS_DIR.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, encoding="utf-8") as f:
            _tips[lang] = json.load(f)


@router.message(F.text.in_(["💡 Совет дня", "💡 Күндүн кеңеши"]))
async def show_tip(message: Message, db_user=None, session=None, t=None, lang="ru", **kwargs):
    if not _tips:
        load_tips()

    tips = _tips.get(lang, _tips.get("ru", []))
    if not tips:
        await message.answer("No tips available yet.")
        return

    if session and db_user:
        last_idx = await crud.get_last_tip_index(session, db_user.id)
        next_idx = (last_idx + 1) % len(tips)
        await crud.log_tip_sent(session, db_user.id, next_idx)
    else:
        next_idx = 0

    if next_idx >= len(tips):
        await message.answer(t("tip_no_more"))
        return

    await message.answer(t("tip_title", tip=tips[next_idx]))
