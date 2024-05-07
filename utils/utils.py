from __future__ import annotations

from telegram_bot_calendar import DetailedTelegramCalendar
from request_to_api.request import *
from typing import List, Dict
import json
from loguru import logger
from telebot import types
import os

path = os.path.abspath(os.path.join('logs', f'debug.{datetime.datetime.now().date()}.log'))
logger.add(path,
           format="{time} {level} {message}",
           level='DEBUG', rotation='3 MB',
           compression='zip')


@logger.catch
def city_founding(city) -> List | None:
    """
    :param city: Имя локации.
    :return: Список с районами
    """
    logger.info(f"utils.utils.city_founding - city: {city}")
    url = "locations/v3/search"
    querystring = {"q": city, "locale": "ru_RU"}
    response = api_request(url, querystring, 'GET')
    if response:
        data = json.loads(response)
        locations = list()
        for city_dict in data['sr']:
            if 'gaiaId' in city_dict:
                locations.append({"id": city_dict['gaiaId'], "name": city_dict['regionNames']['shortName']})
        logger.info(f"utils.utils.city_founding - locations list {locations}")
        return locations
    return response


@logger.catch
def city_markup(city="new york") -> types.InlineKeyboardMarkup:
    """
    Создаёт и возвращает клавиатуру, из локаций в 'city_founding'
    """
    logger.info(f"utils.utils.city_markup - city {city}")
    cities = city_founding(city)
    if cities:
        destinations = types.InlineKeyboardMarkup()
        for city in cities:
            destinations.add(types.InlineKeyboardButton(text=city['name'],
                                                        callback_data=f"ID Location: {city['id']}"))
        return destinations
    else:
        return None


@logger.catch
def currency_markup() -> types.InlineKeyboardMarkup:
    """
    Создаёт и возвращает клавиатуру с валютами
    """
    logger.info(f"utils.utils.currency_markup")
    currency_dict = {'Евро': "EUR", 'Рубли': "RUB", 'Доллары': "USD", 'Фунты': "GBP"}
    currency = types.InlineKeyboardMarkup()
    for name, curr in currency_dict.items():
        currency.add(types.InlineKeyboardButton(text=name, callback_data=f"Currency: {curr}"))
    return currency


@logger.catch
def yes_no_markup() -> types.InlineKeyboardMarkup:
    """
    Создаёт и возвращает клавиатуру с ответами (Да/Нет)
    """
    logger.info(f"utils.utils.yes_no_markup")
    answers_dict = {'Да': 'Да', 'Нет': 'Нет'}
    answers = types.InlineKeyboardMarkup()
    for name, answer in answers_dict.items():
        answers.add(types.InlineKeyboardButton(text=name, callback_data=f"Ответ: {answer}"))
    return answers


@logger.catch
def info_hotel(id: int, currency='USD') -> Dict[str: str] | None:
    """
    Собирает информацию об отеле
    :param id: id отеля
    :param currency: валюта. По умолчанию USD
    :return: Словарь с фото, рейтингом и адресом
    """
    logger.info(f"utils.utils.info_hotel - id: {id}, currency: {currency}")
    url = "properties/v2/detail"
    payload = {
        "currency": currency,
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id
    }
    response = api_request(url, payload, 'POST')
    if response:
        logger.info(f"utils.utils.info_hotel - {response}")
        data = json.loads(response)
        urls_photo = [i_photo['image']['url'] for i_photo in data['data']['propertyInfo']['propertyGallery']['images']]
        rating = data['data']['propertyInfo']['summary']['overview']['propertyRating']
        if rating is not None:
            rating = rating['rating']
        else:
            rating = 0
        address = data['data']['propertyInfo']['summary']['location']['address']['addressLine']
        data = {'photo': urls_photo, 'rating': rating, 'address': address}
        return data
    return response


@logger.catch
def calendar_markup(num: int) -> tuple:
    """
    Создаёт календарь для выбора даты
    :param num: Принимает порядковый номер календаря
    :return: кортеж с датой
    """
    logger.info(f"utils.utils.calendar_markup number of calendar(1/0) - {num}")
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=num).build()
    return calendar


@logger.catch
def get_course_currency(amount: int, old_currency: str, new_currency: str) -> int:
    logger.info(f'utils.utils.get_course_currency - amount {amount}, old_currency {old_currency}, new currency {new_currency}')
    url = "https://api.apilayer.com/currency_data/convert?to={to_}&from={from_}&amount={amount}".format(
        from_=old_currency,
        to_=new_currency,
        amount=amount)
    headers = {"apikey": 'ke8GOvzQK3JB5sbK3G0ujmd5xCm5GJTX'}
    response = requests.get(url, headers=headers)
    if response.status_code == requests.codes.ok:
        data = json.loads(response.text)
        return round(int(data['result']))
    else:
        logger.error(f'utils.utils.get_course_currency - {response.text}')
        return 'Ошибка сервера API Layer'


@logger.catch
def filter_markup():
    """Создаёт клавиатуру с фильтром для поиска"""
    logger.info(f"utils.utils.filter_markup")
    filtres_dict = {'Цена + наш выбор': 'PRICE_RELEVANT',
                    'Оценка гостей': 'REVIEW',
                    "Расстояние от центра города": "DISTANCE",
                    "Количество звезд": "PROPERTY_CLASS"}
    filtres = types.InlineKeyboardMarkup()
    for description, filter in filtres_dict.items():
        filtres.add(types.InlineKeyboardButton(text=description, callback_data=f"Фильтр: {filter}"))
    return filtres
