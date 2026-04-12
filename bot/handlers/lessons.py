from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.db import crud
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.lesson_nav import lesson_list_keyboard, lesson_nav_keyboard, quiz_keyboard
from bot.services.lesson_engine import (
    chunk_lesson,
    get_lesson_list,
    get_quiz,
    load_lesson_content,
    LESSON_SLUGS,
)
from bot.services.scoring import POINTS_LESSON_COMPLETE, POINTS_QUIZ_PERFECT

router = Router()


@router.message(F.text.in_(["📚 Уроки", "📚 Сабактар"]))
async def show_lessons(message: Message, db_user=None, session=None, t=None, lang="ru", **kwargs):
    lessons = get_lesson_list(lang)
    completed = await crud.get_completed_lessons(session, db_user.id) if session else []
    kb = lesson_list_keyboard(lessons, completed, db_user.current_lesson if db_user else 0, t)
    await message.answer(t("lessons_title"), reply_markup=kb)


@router.callback_query(lambda c: c.data == "lessons:list")
async def back_to_lessons(callback: CallbackQuery, db_user=None, session=None, t=None, lang="ru", **kwargs):
    lessons = get_lesson_list(lang)
    completed = await crud.get_completed_lessons(session, db_user.id) if session else []
    kb = lesson_list_keyboard(lessons, completed, db_user.current_lesson if db_user else 0, t)
    await callback.message.edit_text(t("lessons_title"), reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lesson:") and c.data != "lesson:locked")
async def open_lesson(callback: CallbackQuery, db_user=None, session=None, t=None, lang="ru", **kwargs):
    slug = callback.data.split(":")[1]
    content = load_lesson_content(slug, lang)
    if not content:
        await callback.answer("Lesson not found", show_alert=True)
        return

    chunks = chunk_lesson(content)
    quiz = get_quiz(slug)
    kb = lesson_nav_keyboard(slug, 0, len(chunks), quiz is not None, t)
    await callback.message.edit_text(chunks[0], reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "lesson:locked")
async def locked_lesson(callback: CallbackQuery, **kwargs):
    await callback.answer("🔒", show_alert=False)


@router.callback_query(lambda c: c.data and c.data.startswith("lpage:"))
async def lesson_page(callback: CallbackQuery, t=None, lang="ru", **kwargs):
    _, slug, page_str = callback.data.split(":")
    page = int(page_str)
    content = load_lesson_content(slug, lang)
    if not content:
        await callback.answer()
        return
    chunks = chunk_lesson(content)
    page = min(page, len(chunks) - 1)
    quiz = get_quiz(slug)
    kb = lesson_nav_keyboard(slug, page, len(chunks), quiz is not None, t)
    await callback.message.edit_text(chunks[page], reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("quiz:"))
async def start_quiz(callback: CallbackQuery, lang="ru", **kwargs):
    slug = callback.data.split(":")[1]
    quiz = get_quiz(slug)
    if not quiz:
        # No quiz — mark lesson complete directly
        await _complete_lesson(callback, slug)
        return
    q = quiz[0]
    question_text = q["question"][lang] if isinstance(q["question"], dict) else q["question"]
    options = q["options"][lang] if isinstance(q["options"], dict) else q["options"]
    kb = quiz_keyboard(options, slug, 0)
    await callback.message.edit_text(f"📝 {question_text}", reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("qans:"))
async def quiz_answer(callback: CallbackQuery, db_user=None, session=None, t=None, lang="ru", **kwargs):
    _, slug, q_idx_str, ans_idx_str = callback.data.split(":")
    q_idx = int(q_idx_str)
    ans_idx = int(ans_idx_str)

    quiz = get_quiz(slug)
    if not quiz or q_idx >= len(quiz):
        await callback.answer()
        return

    q = quiz[q_idx]
    correct = q["correct"]
    is_correct = ans_idx == correct
    correct_text = q["options"][lang][correct] if isinstance(q["options"], dict) else q["options"][correct]

    if is_correct:
        feedback = t("quiz_correct", points=POINTS_QUIZ_PERFECT)
    else:
        feedback = t("quiz_wrong", answer=correct_text)

    # Move to next question or complete
    if q_idx + 1 < len(quiz):
        next_q = quiz[q_idx + 1]
        question_text = next_q["question"][lang] if isinstance(next_q["question"], dict) else next_q["question"]
        options = next_q["options"][lang] if isinstance(next_q["options"], dict) else next_q["options"]
        kb = quiz_keyboard(options, slug, q_idx + 1)
        await callback.message.edit_text(f"{feedback}\n\n📝 {question_text}", reply_markup=kb)
    else:
        await callback.message.edit_text(feedback)
        await _complete_lesson(callback, slug, db_user=db_user, session=session, t=t)

    await callback.answer()


async def _complete_lesson(callback, slug, db_user=None, session=None, t=None, **kwargs):
    if session and db_user:
        await crud.complete_lesson(session, db_user.id, slug)
        await crud.add_points(session, db_user.id, POINTS_LESSON_COMPLETE)
        idx = LESSON_SLUGS.index(slug) if slug in LESSON_SLUGS else 0
        await crud.advance_lesson(session, db_user.id, idx + 1)
    if t:
        # Build keyboard with "Next lesson" button if there are more lessons
        kb_buttons = []
        idx = LESSON_SLUGS.index(slug) if slug in LESSON_SLUGS else 0
        if idx + 1 < len(LESSON_SLUGS):
            next_slug = LESSON_SLUGS[idx + 1]
            kb_buttons.append([InlineKeyboardButton(
                text=t("next_lesson"), callback_data=f"lesson:{next_slug}"
            )])
        kb_buttons.append([InlineKeyboardButton(
            text=t("back"), callback_data="lessons:list"
        )])
        kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
        await callback.message.answer(
            t("lesson_complete"),
            reply_markup=kb,
        )
