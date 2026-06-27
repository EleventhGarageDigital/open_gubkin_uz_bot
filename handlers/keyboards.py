from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import DIRECTIONS, AVAILABLE_DATES, AVAILABLE_TIMES

WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def categories_keyboard() -> InlineKeyboardMarkup:
    categories = []
    for key, info in DIRECTIONS.items():
        if info["category"] not in categories:
            categories.append(info["category"])

    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category, callback_data=f"cat:{category}")
    builder.adjust(1)
    return builder.as_markup()


def directions_keyboard(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, info in DIRECTIONS.items():
        if info["category"] == category:
            builder.button(text=info["title"], callback_data=f"dir:{key}")
    builder.button(text="⬅️ Назад", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()


def dates_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for date_str in AVAILABLE_DATES:
        from datetime import datetime

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = WEEKDAYS_RU[date_obj.weekday()]
        label = f"{date_obj.strftime('%d.%m.%Y')} ({weekday})"
        builder.button(text=label, callback_data=f"date:{date_str}")
    builder.button(text="⬅️ Назад", callback_data="back_to_directions")
    builder.adjust(1)
    return builder.as_markup()


def times_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for time_str in AVAILABLE_TIMES:
        builder.button(text=time_str, callback_data=f"time:{time_str}")
    builder.button(text="⬅️ Назад", callback_data="back_to_dates")
    builder.adjust(3)
    return builder.as_markup()


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить запись", callback_data="confirm_yes")
    builder.button(text="❌ Начать заново", callback_data="confirm_no")
    builder.adjust(1)
    return builder.as_markup()
