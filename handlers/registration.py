import logging
import re

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import DIRECTIONS, ADMIN_IDS
from handlers.states import Registration
from handlers.keyboards import (
    categories_keyboard,
    directions_keyboard,
    dates_keyboard,
    times_keyboard,
    confirm_keyboard,
)
from utils.sheets import add_registration

logger = logging.getLogger(__name__)
router = Router()

# Простая проверка ФИО: минимум 2 слова, только буквы (рус/лат), дефисы и пробелы
FULL_NAME_PATTERN = re.compile(r"^[А-ЯЁа-яёA-Za-z\-]+(\s[А-ЯЁа-яёA-Za-z\-]+){1,3}$")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👋 Здравствуйте! Это бот регистрации на <b>День открытых дверей "
        "РГУ нефти и газа (НИУ) имени И.М. Губкина 2024</b>.\n\n"
        "Чтобы записаться, введите, пожалуйста, своё <b>ФИО полностью</b> "
        "(например: Иванов Иван Иванович):"
    )
    await state.set_state(Registration.waiting_full_name)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Регистрация отменена. Чтобы начать заново — отправьте /start")


@router.message(Registration.waiting_full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    full_name = re.sub(r"\s+", " ", (message.text or "").strip())

    if not FULL_NAME_PATTERN.match(full_name):
        await message.answer(
            "⚠️ Пожалуйста, введите ФИО корректно — минимум фамилию и имя, "
            "только буквы (например: Иванов Иван Иванович)."
        )
        return

    await state.update_data(full_name=full_name)
    await message.answer(
        f"Спасибо, <b>{full_name}</b>!\n\n"
        "Теперь выберите направление подготовки:",
        reply_markup=categories_keyboard(),
    )
    await state.set_state(Registration.choosing_category)


@router.callback_query(Registration.choosing_category, F.data.startswith("cat:"))
async def process_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split("cat:", 1)[1]
    await state.update_data(category=category)
    await callback.message.edit_text(
        f"Категория: <b>{category}</b>\n\nВыберите конкретное направление:",
        reply_markup=directions_keyboard(category),
    )
    await state.set_state(Registration.choosing_direction)
    await callback.answer()


@router.callback_query(Registration.choosing_direction, F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Выберите направление подготовки:",
        reply_markup=categories_keyboard(),
    )
    await state.set_state(Registration.choosing_category)
    await callback.answer()


@router.callback_query(Registration.choosing_direction, F.data.startswith("dir:"))
async def process_direction(callback: CallbackQuery, state: FSMContext) -> None:
    direction_key = callback.data.split("dir:", 1)[1]
    direction_info = DIRECTIONS.get(direction_key)

    if not direction_info:
        await callback.answer("Направление не найдено, попробуйте снова", show_alert=True)
        return

    await state.update_data(
        direction_key=direction_key, direction_title=direction_info["title"]
    )
    await callback.message.edit_text(
        f"Направление: <b>{direction_info['title']}</b>\n\n"
        "Теперь выберите дату посещения:",
        reply_markup=dates_keyboard(),
    )
    await state.set_state(Registration.choosing_date)
    await callback.answer()


@router.callback_query(Registration.choosing_date, F.data == "back_to_directions")
async def back_to_directions(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("category", "")
    await callback.message.edit_text(
        f"Категория: <b>{category}</b>\n\nВыберите конкретное направление:",
        reply_markup=directions_keyboard(category),
    )
    await state.set_state(Registration.choosing_direction)
    await callback.answer()


@router.callback_query(Registration.choosing_date, F.data.startswith("date:"))
async def process_date(callback: CallbackQuery, state: FSMContext) -> None:
    visit_date = callback.data.split("date:", 1)[1]
    await state.update_data(visit_date=visit_date)
    await callback.message.edit_text(
        f"Дата визита: <b>{visit_date}</b>\n\nВыберите удобное время:",
        reply_markup=times_keyboard(),
    )
    await state.set_state(Registration.choosing_time)
    await callback.answer()


@router.callback_query(Registration.choosing_time, F.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Выберите дату визита:",
        reply_markup=dates_keyboard(),
    )
    await state.set_state(Registration.choosing_date)
    await callback.answer()


@router.callback_query(Registration.choosing_time, F.data.startswith("time:"))
async def process_time(callback: CallbackQuery, state: FSMContext) -> None:
    visit_time = callback.data.split("time:", 1)[1]
    await state.update_data(visit_time=visit_time)

    data = await state.get_data()
    summary = (
        "📋 <b>Проверьте данные перед подтверждением:</b>\n\n"
        f"👤 ФИО: <b>{data['full_name']}</b>\n"
        f"🎓 Направление: <b>{data['direction_title']}</b>\n"
        f"📂 Категория: <b>{data['category']}</b>\n"
        f"📅 Дата: <b>{data['visit_date']}</b>\n"
        f"🕒 Время: <b>{visit_time}</b>\n\n"
        "Всё верно?"
    )
    await callback.message.edit_text(summary, reply_markup=confirm_keyboard())
    await state.set_state(Registration.confirming)
    await callback.answer()


@router.callback_query(Registration.confirming, F.data == "confirm_no")
async def restart_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Регистрация сброшена. Отправьте /start, чтобы начать заново."
    )
    await callback.answer()


@router.callback_query(Registration.confirming, F.data == "confirm_yes")
async def confirm_registration(
    callback: CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    data = await state.get_data()
    user = callback.from_user

    try:
        add_registration(
            full_name=data["full_name"],
            direction_title=data["direction_title"],
            category=data["category"],
            visit_date=data["visit_date"],
            visit_time=data["visit_time"],
            telegram_id=user.id,
            telegram_username=user.username,
        )
    except Exception:
        logger.exception("Ошибка записи в Google Sheets")
        await callback.message.edit_text(
            "😔 Произошла ошибка при сохранении данных. "
            "Пожалуйста, попробуйте ещё раз позже или напишите организаторам."
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "✅ <b>Вы успешно записаны на День открытых дверей!</b>\n\n"
        f"📅 {data['visit_date']} в {data['visit_time']}\n"
        f"🎓 {data['direction_title']}\n\n"
        "До встречи в РГУ нефти и газа (НИУ) имени И.М. Губкина! 🛢️🎓\n"
        "Если планы изменятся — отправьте /start, чтобы перезаписаться."
    )
    await callback.answer("Запись подтверждена ✅")

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "🆕 <b>Новая запись на День открытых дверей</b>\n\n"
                f"👤 {data['full_name']}\n"
                f"🎓 {data['direction_title']}\n"
                f"📅 {data['visit_date']} в {data['visit_time']}\n"
                f"💬 @{user.username if user.username else user.id}",
            )
        except Exception:
            logger.exception("Не удалось отправить уведомление админу %s", admin_id)

    await state.clear()
