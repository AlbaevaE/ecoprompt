from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def practice_result_keyboard(
    task_id: str, ai_remaining: int, t
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=t("practice_retry"), callback_data=f"practice:retry:{task_id}"),
            InlineKeyboardButton(text=t("practice_next"), callback_data="practice:next"),
        ]
    ]
    if ai_remaining > 0:
        buttons.append([
            InlineKeyboardButton(
                text=t("practice_ai_feedback", remaining=ai_remaining),
                callback_data=f"practice:ai:{task_id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
