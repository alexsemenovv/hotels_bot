from __future__ import annotations

import peewee
from loader import bot
from database.models import *
from utils.utils import *
from telebot import types
from states.user_info import UserInfoState

@logger.catch
@bot.message_handler(commands=['history'])
def return_history(message: types.Message) -> None:
    logger.info(f'custom handlers.history.return_history - {message}')
    bot.set_state(message.from_user.id, UserInfoState.user_command, message.chat.id)
    try:
        with db:
            users = sorted(User.select().where(User.tg_id == message.from_user.id), key=lambda x: User.datetime_query, reverse=True)
            if len(users) > 10:
                len_users = 10
            else:
                len_users = len(users)
            for i in range(len_users):
                bot.send_message(message.from_user.id,
                                 f"Запрос: {users[i].query_command}\nВремя и дата запроса: {users[i].datetime_query}\nВалюта: {users[i].currency}\n"
                                 f"Город поиска: {users[i].city}\nID локации: {users[i].id_location}\nКоличество взрослых: {users[i].adults}\n"
                                 f"Дети: {users[i].children}\nДата заезда: {users[i].checkin}\nДата выезда: {users[i].checkout}\n"
                                 f"Количество дней: {users[i].count_days}\nКоличество выводимых результатов: {users[i].count_result}"
                                 )
    except peewee.OperationalError as error:
        logger.error(f'custom handlers.history.return_history - {error}')
        bot.send_message(message.from_user.id, 'Данных об истории запросов не найдено.\nСначала выполните запрос')