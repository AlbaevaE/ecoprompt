from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.db.crud import set_language
from bot.keyboards.main_menu import language_keyboard, main_menu
from bot.middlewares.i18n import t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, **kwargs):
    await message.answer(
        t("choose_language"),
        reply_markup=language_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def on_language_selected(callback: CallbackQuery, db_user=None, session=None, **kwargs):
    lang = callback.data.split(":")[1]
    if session and db_user:
        await set_language(session, db_user.id, lang)
        db_user.language = lang

    tr = lambda key, **kw: t(key, lang, **kw)
    await callback.message.edit_text(tr("welcome"))
    await callback.message.answer(
        tr("menu_lessons"),
        reply_markup=main_menu(tr),
    )
    await callback.answer()
