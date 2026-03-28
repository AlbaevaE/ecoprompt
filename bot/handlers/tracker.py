from aiogram import F, Router
from aiogram.types import Message

from bot.db import crud
from bot.services.impact_calculator import format_impact
from bot.services.lesson_engine import LESSON_SLUGS

router = Router()


@router.message(F.text.in_(["📊 Мои достижения", "📊 Жетишкендиктерим"]))
async def show_stats(message: Message, db_user=None, session=None, t=None, **kwargs):
    if not db_user or not session:
        return

    completed = await crud.get_completed_lessons(session, db_user.id)
    impact = format_impact(db_user.total_tokens_saved)

    from sqlalchemy import select, func
    from bot.db.models import PracticeAttempt
    result = await session.execute(
        select(func.count()).where(PracticeAttempt.user_id == db_user.id)
    )
    practice_count = result.scalar() or 0

    await message.answer(
        t(
            "stats_title",
            tokens_saved=db_user.total_tokens_saved,
            points=db_user.total_points,
            lessons_done=len(completed),
            lessons_total=len(LESSON_SLUGS),
            practice_count=practice_count,
            streak=db_user.streak_days,
            wh=impact["wh"],
            ml=impact["ml"],
            wh_1k=impact["wh_1k"],
            ml_1k=impact["ml_1k"],
        )
    )
