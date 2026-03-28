from aiogram import F, Router
from aiogram.types import Message

from bot.db import crud

router = Router()

MEDALS = ["🥇", "🥈", "🥉"]


@router.message(F.text.in_(["🏆 Таблица лидеров", "🏆 Лидерлер тизмеси"]))
async def show_leaderboard(message: Message, db_user=None, session=None, t=None, **kwargs):
    if not session or not db_user:
        return

    top = await crud.get_leaderboard(session, limit=10)
    rank = await crud.get_user_rank(session, db_user.id)

    text = t("leaderboard_title")
    for i, user in enumerate(top):
        medal = MEDALS[i] if i < 3 else f"{i + 1}."
        name = f"@{user.username}" if user.username else f"User #{user.telegram_id}"
        text += t(
            "leaderboard_row",
            medal=medal,
            name=name,
            points=user.total_points,
            tokens=user.total_tokens_saved,
        )

    text += t(
        "leaderboard_you",
        rank=rank,
        points=db_user.total_points,
    )
    await message.answer(text)
