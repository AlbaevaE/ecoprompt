import json
import random
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.config import settings
from bot.db import crud
from bot.keyboards.practice_kb import practice_result_keyboard
from bot.services.impact_calculator import format_impact
from bot.services.llm import get_ai_feedback
from bot.services.prompt_evaluator import evaluate_prompt
from bot.services.scoring import streak_bonus

router = Router()

TASKS_PATH = Path(__file__).parent.parent / "content" / "practice_tasks" / "tasks.json"
_tasks: list[dict] = []


def load_tasks() -> None:
    global _tasks
    if TASKS_PATH.exists():
        with open(TASKS_PATH, encoding="utf-8") as f:
            _tasks = json.load(f)


def get_random_task(exclude_id: str | None = None) -> dict | None:
    if not _tasks:
        load_tasks()
    available = [t for t in _tasks if t["id"] != exclude_id] if exclude_id else _tasks
    return random.choice(available) if available else None


def get_task_by_id(task_id: str) -> dict | None:
    if not _tasks:
        load_tasks()
    for t in _tasks:
        if t["id"] == task_id:
            return t
    return None


class PracticeState(StatesGroup):
    waiting_prompt = State()


@router.message(F.text.in_(["✏️ Практика", "✏️ Машыгуу"]))
async def start_practice(message: Message, state: FSMContext, t=None, lang="ru", **kwargs):
    task = get_random_task()
    if not task:
        await message.answer("No practice tasks available yet.")
        return
    desc = task["description"].get(lang, task["description"].get("ru", ""))
    await state.set_state(PracticeState.waiting_prompt)
    await state.update_data(task_id=task["id"])
    await message.answer(
        t("practice_task", task_description=desc, baseline=task["baseline_tokens"])
    )


@router.callback_query(lambda c: c.data == "practice:next")
async def next_practice(callback: CallbackQuery, state: FSMContext, t=None, lang="ru", **kwargs):
    data = await state.get_data()
    prev_id = data.get("task_id")
    task = get_random_task(exclude_id=prev_id)
    if not task:
        await callback.answer("No more tasks", show_alert=True)
        return
    desc = task["description"].get(lang, task["description"].get("ru", ""))
    await state.set_state(PracticeState.waiting_prompt)
    await state.update_data(task_id=task["id"])
    await callback.message.answer(
        t("practice_task", task_description=desc, baseline=task["baseline_tokens"])
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("practice:retry:"))
async def retry_practice(callback: CallbackQuery, state: FSMContext, t=None, lang="ru", **kwargs):
    task_id = callback.data.split(":")[2]
    task = get_task_by_id(task_id)
    if not task:
        await callback.answer("Task not found", show_alert=True)
        return
    desc = task["description"].get(lang, task["description"].get("ru", ""))
    await state.set_state(PracticeState.waiting_prompt)
    await state.update_data(task_id=task["id"])
    await callback.message.answer(
        t("practice_task", task_description=desc, baseline=task["baseline_tokens"])
    )
    await callback.answer()


@router.message(PracticeState.waiting_prompt)
async def evaluate_user_prompt(
    message: Message, state: FSMContext, db_user=None, session=None, t=None, lang="ru", **kwargs
):
    data = await state.get_data()
    task_id = data.get("task_id")
    task = get_task_by_id(task_id)
    if not task:
        await message.answer("Task not found.")
        await state.clear()
        return

    user_prompt = message.text
    result = evaluate_prompt(user_prompt, task)

    # Check ethics
    if result["has_ethics_issue"]:
        await message.answer(t("practice_ethics_warning"))

    # Save to DB
    if session and db_user:
        await crud.save_practice_attempt(
            session,
            user_id=db_user.id,
            task_id=task_id,
            user_prompt=user_prompt,
            token_count=result["token_count"],
            reference_token_count=result["baseline_tokens"],
            tokens_saved=result["tokens_saved"],
            quality_score=result["quality_score"],
            efficiency_score=result["efficiency_score"],
            points_earned=result["points_earned"],
        )
        await crud.add_points(session, db_user.id, result["points_earned"])
        if result["tokens_saved"] > 0:
            await crud.add_tokens_saved(session, db_user.id, result["tokens_saved"])
        streak = await crud.update_streak(session, db_user.id)
        bonus = streak_bonus(streak)
        if bonus > 0:
            await crud.add_points(session, db_user.id, bonus)

    impact = format_impact(result["tokens_saved"])
    ai_can = await crud.check_ai_feedback_limit(
        session, db_user.id, settings.ai_feedback_daily_limit
    ) if session and db_user else False
    remaining = settings.ai_feedback_daily_limit - (db_user.ai_feedback_used_today if db_user else 0)

    kb = practice_result_keyboard(task_id, remaining if ai_can else 0, t)
    await message.answer(
        t(
            "practice_result",
            user_tokens=result["token_count"],
            baseline=result["baseline_tokens"],
            saved=result["tokens_saved"],
            percent=result["savings_pct"],
            quality=result["quality_score"],
            points=result["points_earned"],
            wh=impact["wh"],
            ml=impact["ml"],
        ),
        reply_markup=kb,
    )
    await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith("practice:ai:"))
async def ai_feedback(callback: CallbackQuery, db_user=None, session=None, t=None, lang="ru", **kwargs):
    task_id = callback.data.split(":")[2]
    task = get_task_by_id(task_id)
    if not task:
        await callback.answer("Task not found", show_alert=True)
        return

    if session and db_user:
        can_use = await crud.check_ai_feedback_limit(
            session, db_user.id, settings.ai_feedback_daily_limit
        )
        if not can_use:
            await callback.answer(
                t("practice_ai_limit", limit=settings.ai_feedback_daily_limit),
                show_alert=True,
            )
            return
        await crud.use_ai_feedback(session, db_user.id)

    desc = task["description"].get(lang, task["description"].get("ru", ""))
    # Get the last prompt from state or message — use callback's message text
    feedback = await get_ai_feedback("(user prompt from last attempt)", desc, lang)
    if feedback:
        await callback.message.answer(t("ai_feedback_result", feedback=feedback))
    else:
        await callback.message.answer("AI feedback is not available.")
    await callback.answer()
