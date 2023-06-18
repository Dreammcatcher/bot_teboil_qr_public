from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    send_message = State()
    press_update = State()
    enter = State()
    append_user = State()
