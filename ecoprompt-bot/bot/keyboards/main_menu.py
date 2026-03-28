from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Кыргызча 🇰🇬", callback_data="lang:ky"),
            InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang:ru"),
        ]
    ])


def main_menu(t) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu_lessons")), KeyboardButton(text=t("menu_practice"))],
            [KeyboardButton(text=t("menu_stats")), KeyboardButton(text=t("menu_tip"))],
            [KeyboardButton(text=t("menu_resources")), KeyboardButton(text=t("menu_settings"))],
        ],
        resize_keyboard=True,
    )
