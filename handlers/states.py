from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_full_name = State()
    choosing_category = State()
    choosing_direction = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()
