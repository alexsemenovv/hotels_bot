import random
from loader import bot
from states.user_info import UserInfoState
from telegram_bot_calendar import LSTEP
from handlers.custom_handlers import lower, high, custom
from database.models import *
from utils.utils import *
from telebot import types


@logger.catch
@bot.message_handler(commands=['low', 'high', 'custom'])
def start(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.start')
    """Отвечает на команды low, high, custom"""
    bot.set_state(message.from_user.id, UserInfoState.user_command)
    with bot.retrieve_data(message.from_user.id) as data:
        data['query_command'] = message.text
        data['sort'], data['min price'], data['max price'] = None, None, None
        bot.set_state(message.from_user.id, UserInfoState.currency)
        bot.send_message(message.from_user.id, f"Выберите валюту: ", reply_markup=currency_markup())

@logger.catch
@bot.callback_query_handler(func=lambda message: message.data.startswith('Currency: '))
def currency(message) -> None:
    logger.info(f'custom handlers.survey.currency')
    """Записывает валюту"""
    with bot.retrieve_data(message.from_user.id) as data:
        data['currency'] = message.data[10:]
        if data['query_command'] == '/custom':
            bot.set_state(message.from_user.id, UserInfoState.filter)
            bot.send_message(message.from_user.id, f"Выберите фильтр: ", reply_markup=filter_markup())
        else:
            bot.send_message(message.from_user.id, message.data)
            bot.set_state(message.from_user.id, UserInfoState.city)
            bot.send_message(message.from_user.id, f"Введите город поиска: ")

@logger.catch
@bot.callback_query_handler(func=lambda message: message.data.startswith('Фильтр: '))
def get_filter(message) -> None:
    logger.info(f'custom handlers.survey.get_filter - {message}')
    """Записывает фильтр"""
    with bot.retrieve_data(message.from_user.id) as data:
        data['sort'] = message.data[8:]
    bot.set_state(message.from_user.id, UserInfoState.min_price)
    bot.send_message(message.from_user.id, message.data)
    bot.send_message(message.from_user.id, f"Введите минимальную цену: ")

@logger.catch
@bot.message_handler(state=UserInfoState.min_price)
def get_min_price(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.get_min_price - {message}')
    """Получает минмальную цену диапазона поиска для /custom"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id) as data:
            data['min price'] = message.text
        bot.set_state(message.from_user.id, UserInfoState.max_price, message.chat.id)
        bot.send_message(message.from_user.id, f"Введите максимальную цену: ")
    else:
        bot.send_message(message.from_user.id, 'Введите число: ')

@logger.catch
@bot.message_handler(state=UserInfoState.max_price)
def get_max_price(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.get_max_price - {message}')
    """Получает максимальную цену диапазона поиска для /custom"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id) as data:
            if int(data['min price']) < int(message.text):
                data['max price'] = message.text
                bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
                bot.send_message(message.from_user.id, f"Введите город поиска: ")
            else:
                bot.send_message(message.from_user.id, 'Максимальная цена должна быть больше, чем минимальная!')
    else:
        bot.send_message(message.from_user.id, 'Введите число: ')

@logger.catch
@bot.message_handler(state=UserInfoState.city)
def city(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.city - {message}')
    """Записывает город для поиска"""
    bot.set_state(message.from_user.id, UserInfoState.checkIn, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text
    if city_markup(data['city']):
        bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=city_markup(data['city']))
    else:
        bot.send_message(message.from_user.id, 'Такой город не найден.')



@logger.catch
@bot.callback_query_handler(func=lambda message: message.data.startswith('ID Location:'))
def id_location(message) -> None:
    logger.info(f'custom handlers.survey.id_location - {message}')
    """Записывает ID локации"""
    with bot.retrieve_data(message.from_user.id) as data:
        data['id location'] = message.data[13:]
    bot.send_message(message.from_user.id, message.data)
    bot.set_state(message.from_user.id, UserInfoState.adults, message.from_user.id)
    bot.send_message(message.from_user.id, 'Сколько будет взрослых: ', )


@logger.catch
@bot.message_handler(state=UserInfoState.adults)
def count_adults(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.count_adults - {message}')
    """Записывает количество взрослых"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id) as data:
            data['adults'] = int(message.text)
        bot.send_message(message.from_user.id, "Есть ли дети? ", reply_markup=yes_no_markup())
    else:
        bot.send_message(message.from_user.id, "Укажите пожалуйста число")

@logger.catch
@bot.callback_query_handler(func=lambda message: message.data.startswith('Ответ:'))
def answers(message) -> None:
    logger.info(f'custom handlers.survey.answers - {message}')
    """Проверяет ответ пользователя.
        Если 'да' - вызывает count_children(),
        Если 'нет' - вызывает calendar_markup()"""
    if message.data[7:] == 'Да':
        bot.set_state(message.from_user.id, UserInfoState.children, message.from_user.id)
        bot.send_message(message.from_user.id, 'Укажите возраста детей через пробел: ', )
    else:
        with bot.retrieve_data(message.from_user.id) as data:
            data['count children'] = None
        bot.set_state(message.from_user.id, UserInfoState.checkIn, message.from_user.id)
        bot.send_message(message.from_user.id, 'Выберите дату заезда: ', reply_markup=calendar_markup(0))


@logger.catch
@bot.message_handler(state=UserInfoState.children)
def count_children(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.count_children - {message}')
    """Записывает возрасты детей в список"""
    ages = (message.text).split()
    children_list = [{'age': int(i_age)} for i_age in ages]
    with bot.retrieve_data(message.from_user.id) as data:
        data['children'] = children_list
        data['count children'] = len(children_list)
    bot.set_state(message.from_user.id, UserInfoState.checkIn, message.from_user.id)
    bot.send_message(message.from_user.id, 'Выберите дату заезда: ', reply_markup=calendar_markup(0))


@logger.catch
@bot.callback_query_handler(state=UserInfoState.checkIn, func=DetailedTelegramCalendar.func(calendar_id=0))
def callback_checkin(message: types.CallbackQuery) -> None:
    logger.info(f'custom handlers.survey.callback_checkin - {message}')
    """Получает дату заезда"""
    result, key, step = DetailedTelegramCalendar(calendar_id=0, min_date=datetime.date.today()).process(message.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              message.message.chat.id,
                              message.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(message.from_user.id) as data:
            data['checkIn'] = result
            bot.edit_message_text(f"Дата заезда: {result}",
                                  message.message.chat.id,
                                  message.message.message_id)
            bot.set_state(message.from_user.id, UserInfoState.checkOut)
            bot.send_message(message.from_user.id, 'Когда уезжаем: ', reply_markup=calendar_markup(1))


@logger.catch
@bot.callback_query_handler(state=UserInfoState.checkOut, func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_checkout(message: types.CallbackQuery) -> None:
    logger.info(f'custom handlers.survey.callback_checkout - {message}')
    """Получает дату выезда"""
    with bot.retrieve_data(message.from_user.id) as data:
        result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                     min_date=data['checkIn'] + datetime.timedelta(days=1)).process(message.data)
        if not result and key:
            logger.info(f"Call: callback_checkout params: message: {message} INFO: 'not result and key'")
            bot.edit_message_text(f"Select {LSTEP[step]}",
                                  message.message.chat.id,
                                  message.message.message_id,
                                  reply_markup=key)
        elif result:
            logger.info(f"Call: callback_checkout params: message: {message} INFO: get result")
            data['days_count'] = (result - data['checkIn']).days
            data['checkOut'] = result
            bot.edit_message_text(f"Дата выезда: {result}",
                                  message.message.chat.id,
                                  message.message.message_id)

            bot.set_state(message.from_user.id, UserInfoState.results_size, message.from_user.id)
            bot.send_message(message.from_user.id, 'Сколько результатов вывести? не более 200')


@logger.catch
@bot.message_handler(state=UserInfoState.results_size)
def results_size(message: types.Message) -> None:
    logger.info(f'custom handlers.survey.result_size - {message}')
    """Записывает данные в БД и отправляет информацию по каждому отелю"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            data['resultsSize'] = int(message.text)
            query_command = data['query_command']
            bot.set_state(message.from_user.id, UserInfoState.user_command, message.chat.id)
        except ValueError:
            bot.send_message(message.from_user.id, 'Количество должно быть целым числом')

    if query_command == '/low':
        hotels = lower.get_id_hotels(data)
    elif query_command == '/high':
        hotels = high.check_response(data)
    elif query_command == '/custom':
        hotels = custom.get_id_hotels(data)
    with db:
        db.create_tables([User, Hotel, Photo])
        user = User.create(
            tg_id=message.from_user.id,
            name=message.from_user.first_name,
            username=message.from_user.username,
            query_command=data['query_command'],
            datetime_query=datetime.datetime.now(),
            currency=data['currency'],
            city=data['city'],
            id_location=data['id location'],
            adults=data['adults'],
            children=data['count children'],
            checkin=data['checkIn'],
            checkout=data['checkOut'],
            count_days=data['days_count'],
            count_result=data['resultsSize'],
            filter=data['sort'],
            min_price=data['min price'],
            max_price=data['max price']
        )
    if hotels == 'Ошибка' or hotels is None:
        bot.send_message(message.chat.id, 'По заданным параметрам нет отелей. Попробуйте снова')
    else:
        for i_hotel in hotels:
            hotel = info_hotel(i_hotel['id hotel'])
            if hotel:
                photos_media = list()
                for _ in range(5):
                    photos_media.append(types.InputMediaPhoto(media=random.choice(hotel['photo']))) #выбирает случайные ссылки на фото
                if photos_media:
                    bot.send_media_group(message.chat.id, photos_media)
                else:
                    bot.send_message(message.from_user.id, 'Нет фото для этого отеля')
                logger.info(f'custom handlers.survey.result_size - info about hotel {hotel}')
                bot.send_message(message.chat.id,
                                 f"Ссылка на отель: https://www.hotels.com/h{i_hotel['id hotel']}.Hotel-information\n"
                                 f"Название отеля: {i_hotel['name']}\n"
                                 f"Цена за одну ночь: {i_hotel['price_one_night']} {data['currency']}\n"
                                 f"Общая стоимость: {i_hotel['price_one_night'] * data['days_count']} {data['currency']}\n"
                                 f"Рейтинг: {hotel['rating']}\n"
                                 f"Адрес: {hotel['address']}")

                with db:
                    hotel_db = Hotel.create(
                       hotel_id=i_hotel['id hotel'],
                       user_id=user,
                       name=i_hotel['name'],
                       price=f"{i_hotel['price_one_night']} {data['currency']}",
                       link=f"https://www.hotels.com/h{i_hotel['id hotel']}.Hotel-information",
                       rating=hotel['rating'],
                       address=hotel['address']
                        )
                    new_photo = [{'hotel_id': hotel_db, 'link': i_link, 'user_id': user} for i_link in hotel['photo']]
                    Photo.insert_many(new_photo, ).execute()


