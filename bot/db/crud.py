from datetime import date, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import DailyTipLog, Feedback, LessonCompletion, PracticeAttempt, User


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None = None
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def set_language(session: AsyncSession, user_id: int, language: str) -> None:
    await session.execute(
        update(User).where(User.id == user_id).values(language=language)
    )
    await session.commit()


async def get_completed_lessons(session: AsyncSession, user_id: int) -> list[str]:
    result = await session.execute(
        select(LessonCompletion.lesson_slug).where(
            LessonCompletion.user_id == user_id
        )
    )
    return list(result.scalars().all())


async def complete_lesson(
    session: AsyncSession, user_id: int, lesson_slug: str, quiz_score: int | None = None
) -> None:
    existing = await session.execute(
        select(LessonCompletion).where(
            LessonCompletion.user_id == user_id,
            LessonCompletion.lesson_slug == lesson_slug,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return
    completion = LessonCompletion(
        user_id=user_id, lesson_slug=lesson_slug, quiz_score=quiz_score
    )
    session.add(completion)
    await session.commit()


async def add_points(session: AsyncSession, user_id: int, points: int) -> None:
    await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(total_points=User.total_points + points)
    )
    await session.commit()


async def add_tokens_saved(session: AsyncSession, user_id: int, tokens: int) -> None:
    await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(total_tokens_saved=User.total_tokens_saved + tokens)
    )
    await session.commit()


async def save_practice_attempt(
    session: AsyncSession,
    user_id: int,
    task_id: str,
    user_prompt: str,
    token_count: int,
    reference_token_count: int,
    tokens_saved: int,
    quality_score: float,
    efficiency_score: float,
    points_earned: int,
) -> PracticeAttempt:
    attempt = PracticeAttempt(
        user_id=user_id,
        task_id=task_id,
        user_prompt=user_prompt,
        token_count=token_count,
        reference_token_count=reference_token_count,
        tokens_saved=tokens_saved,
        quality_score=quality_score,
        efficiency_score=efficiency_score,
        points_earned=points_earned,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def advance_lesson(session: AsyncSession, user_id: int, lesson_idx: int) -> None:
    await session.execute(
        update(User)
        .where(User.id == user_id, User.current_lesson < lesson_idx)
        .values(current_lesson=lesson_idx)
    )
    await session.commit()


async def update_streak(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    today = date.today().isoformat()
    if user.last_streak_date == today:
        return user.streak_days
    yesterday = date.fromordinal(date.today().toordinal() - 1).isoformat()
    if user.last_streak_date == yesterday:
        new_streak = user.streak_days + 1
    else:
        new_streak = 1
    await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(streak_days=new_streak, last_streak_date=today)
    )
    await session.commit()
    return new_streak


async def get_leaderboard(session: AsyncSession, limit: int = 10) -> list[User]:
    result = await session.execute(
        select(User).order_by(User.total_points.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_user_rank(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    count_result = await session.execute(
        select(User).where(User.total_points > user.total_points)
    )
    return len(count_result.scalars().all()) + 1


async def check_ai_feedback_limit(session: AsyncSession, user_id: int, daily_limit: int) -> bool:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    today = date.today().isoformat()
    if user.ai_feedback_reset_date != today:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(ai_feedback_used_today=0, ai_feedback_reset_date=today)
        )
        await session.commit()
        return True
    return user.ai_feedback_used_today < daily_limit


async def use_ai_feedback(session: AsyncSession, user_id: int) -> None:
    await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(ai_feedback_used_today=User.ai_feedback_used_today + 1)
    )
    await session.commit()


async def get_last_tip_index(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(
        select(DailyTipLog.tip_index)
        .where(DailyTipLog.user_id == user_id)
        .order_by(DailyTipLog.sent_at.desc())
        .limit(1)
    )
    idx = result.scalar_one_or_none()
    return idx if idx is not None else -1


async def log_tip_sent(session: AsyncSession, user_id: int, tip_index: int) -> None:
    log = DailyTipLog(user_id=user_id, tip_index=tip_index)
    session.add(log)
    await session.commit()


async def save_feedback(
    session: AsyncSession, user_id: int, category: str, text: str
) -> Feedback:
    fb = Feedback(user_id=user_id, category=category, text=text)
    session.add(fb)
    await session.commit()
    await session.refresh(fb)
    return fb
