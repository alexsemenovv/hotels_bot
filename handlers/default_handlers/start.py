from telebot.types import Message
from loader import bot

@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\nМеня зовут Турист-Бот\n"
                          f"Я умею искать отели по заданным параметрам\n"
                          f"Для того чтобы начать поиск, ты можешь посмотреть описание команду, кликнув на команду /help")

