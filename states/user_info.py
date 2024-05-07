from telebot.handler_backends import State, StatesGroup

class UserInfoState(StatesGroup):
    user_command = State()
    city = State()
    currency = State()
    checkIn = State()
    checkOut = State()
    adults = State()
    children = State()
    results_size = State()
    filter = State()
    min_price = State()
    max_price = State()