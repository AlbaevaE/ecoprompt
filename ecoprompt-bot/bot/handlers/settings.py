from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.db.crud import set_language
from bot.keyboards.main_menu import language_keyboard, main_menu
from bot.middlewares.i18n import t as translate

router = Router()


@router.message(F.text.in_(["⚙️ Настройки", "⚙️ Орнотуулар"]))
async def show_settings(message: Message, t=None, **kwargs):
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("settings_language"), callback_data="settings:language")],
    ])
    await message.answer(t("settings_title"), reply_markup=kb)


@router.callback_query(lambda c: c.data == "settings:language")
async def change_language(callback: CallbackQuery, **kwargs):
    await callback.message.edit_text(
        translate("choose_language"),
        reply_markup=language_keyboard(),
    )
    await callback.answer()
