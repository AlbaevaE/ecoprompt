from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def lesson_list_keyboard(
    lessons: list[dict], completed: list[str], current_lesson: int, t
) -> InlineKeyboardMarkup:
    buttons = []
    for i, lesson in enumerate(lessons):
        slug = lesson["slug"]
        title = lesson["title"]
        if slug in completed:
            icon = t("lesson_done")
        else:
            icon = t("lesson_unlocked")
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {i + 1}. {title}",
                callback_data=f"lesson:{slug}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def lesson_nav_keyboard(lesson_slug: str, page: int, total_pages: int, has_quiz: bool, t) -> InlineKeyboardMarkup:
    buttons = []
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"lpage:{lesson_slug}:{page - 1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"lpage:{lesson_slug}:{page + 1}"))
    elif has_quiz:
        nav_row.append(InlineKeyboardButton(text="📝 Тест", callback_data=f"quiz:{lesson_slug}"))
    if nav_row:
        buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text=t("back"), callback_data="lessons:list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def quiz_keyboard(options: list[str], lesson_slug: str, question_idx: int) -> InlineKeyboardMarkup:
    buttons = []
    for i, option in enumerate(options):
        buttons.append([
            InlineKeyboardButton(
                text=option,
                callback_data=f"qans:{lesson_slug}:{question_idx}:{i}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
