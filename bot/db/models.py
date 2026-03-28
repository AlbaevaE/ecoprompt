from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(Text, default="ru")
    total_tokens_saved: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    current_lesson: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_streak_date: Mapped[str | None] = mapped_column(Text)
    ai_feedback_used_today: Mapped[int] = mapped_column(Integer, default=0)
    ai_feedback_reset_date: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    lesson_completions: Mapped[list["LessonCompletion"]] = relationship(
        back_populates="user"
    )
    practice_attempts: Mapped[list["PracticeAttempt"]] = relationship(
        back_populates="user"
    )


class LessonCompletion(Base):
    __tablename__ = "lesson_completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_slug: Mapped[str] = mapped_column(Text, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    quiz_score: Mapped[int | None] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="lesson_completions")


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_saved: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float | None] = mapped_column(Float)
    efficiency_score: Mapped[float | None] = mapped_column(Float)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="practice_attempts")


class DailyTipLog(Base):
    __tablename__ = "daily_tip_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tip_index: Mapped[int] = mapped_column(Integer, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
