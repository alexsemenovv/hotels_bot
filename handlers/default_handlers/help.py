from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку",
            "/low - Вывести дешевые отели",
            "/high - Вывести дорогие отели",
            "/custom - Ручной поиск",
            "/history - история поиска(последние 10 запросов)")

    bot.reply_to(message, "\n".join(text))
