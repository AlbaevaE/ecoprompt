from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.db import crud
from bot.keyboards.main_menu import main_menu

router = Router()

CATEGORIES = {
    "feedback:materials": "feedback_materials",
    "feedback:curriculum": "feedback_curriculum",
    "feedback:bug": "feedback_bug",
    "feedback:other": "feedback_other",
}


class FeedbackState(StatesGroup):
    waiting_text = State()


def feedback_keyboard(t) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("feedback_materials"), callback_data="feedback:materials")],
        [InlineKeyboardButton(text=t("feedback_curriculum"), callback_data="feedback:curriculum")],
        [InlineKeyboardButton(text=t("feedback_bug"), callback_data="feedback:bug")],
        [InlineKeyboardButton(text=t("feedback_other"), callback_data="feedback:other")],
        [InlineKeyboardButton(text=t("back"), callback_data="feedback:cancel")],
    ])


@router.message(F.text.in_(["💬 Обратная связь", "💬 Кайтарым байланыш"]))
async def show_feedback_menu(message: Message, state: FSMContext, t=None, **kwargs):
    await state.clear()
    await message.answer(t("feedback_title"), reply_markup=feedback_keyboard(t))


@router.callback_query(lambda c: c.data and c.data.startswith("feedback:"))
async def handle_feedback_category(
    callback: CallbackQuery, state: FSMContext, t=None, **kwargs
):
    action = callback.data
    if action == "feedback:cancel":
        await state.clear()
        await callback.message.answer(t("feedback_cancel"), reply_markup=main_menu(t))
        await callback.answer()
        return

    category_key = CATEGORIES.get(action)
    if not category_key:
        await callback.answer()
        return

    await state.set_state(FeedbackState.waiting_text)
    await state.update_data(category=action.split(":")[1])
    await callback.message.answer(t("feedback_prompt"))
    await callback.answer()


@router.message(FeedbackState.waiting_text)
async def receive_feedback_text(
    message: Message, state: FSMContext, db_user=None, session=None, t=None, **kwargs
):
    data = await state.get_data()
    category = data.get("category", "other")

    if session and db_user:
        await crud.save_feedback(session, db_user.id, category, message.text)

    await state.clear()
    await message.answer(t("feedback_thanks"), reply_markup=main_menu(t))
