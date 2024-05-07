from __future__ import annotations

from utils.utils import *


@logger.catch
def get_id_hotels(user_data, max_price, min_price) -> List | None:
    """
    :param user_data: словарь с данными опроса пользователя
    :param min_price: нижний лимит по умолчанию
    :param max_price: верхний лимит по умолчанию
    :return: response
    """
    logger.info(f"custom handlers.higher.get_id_hotels params: {user_data}")
    url = "properties/v2/list"
    payload = {'currency': user_data['currency'],
               'eapid': 1,
               'locale': 'ru_RU',
               'siteId': 300000001,
               'destination': {
                   'regionId': user_data['id location']
               },
               'checkInDate': {'day': int(user_data['checkIn'].strftime("%d")),
                               'month': int(user_data['checkIn'].strftime("%m")),
                               'year': int(user_data['checkIn'].strftime("%Y"))
                               },
               'checkOutDate': {'day': int(user_data['checkOut'].strftime("%d")),
                                'month': int(user_data['checkOut'].strftime("%m")),
                                'year': int(user_data['checkOut'].strftime("%Y"))
                                },
               'resultsStartingIndex': 0,
               'resultsSize': 200,
               'sort': 'PRICE_LOW_TO_HIGH',
               'filters': {'price': {'max': max_price,
                                     'min': min_price}}
               }

    if user_data['count children'] is None:
        logger.info(f"custom handlers.higher.get_id_hotels - data without children")
        payload['rooms'] = [{'adults': user_data['adults']}]
    else:
        logger.info(f"custom handlers.higher.get_id_hotels - data with {user_data['children']} children")
        payload['rooms'] = [{'adults': user_data['adults'], 'children': user_data['children']}]
    response = api_request(url, payload, 'POST')
    return response


def check_response(user_data: dict) -> List | str:
    max_price = 50_000
    min_price = 10_000
    while True:
        response = get_id_hotels(user_data, max_price, min_price)
        data = json.loads(response)
        if ('errors' in data and max_price > 1000) or ('errors' not in data and user_data['resultsSize'] > len(data['data']['propertySearch']['properties'])):
            max_price = min_price
            min_price = max_price // 2
            logger.info(f'custom handlers.high.check_response: max_price = {max_price}, min_price = {min_price}')
        elif 'errors' in data and max_price < 1000:
            logger.error(f'custom handlers.high.check_response: нет данных по заданным параметрам')
            return 'Ошибка'
        elif user_data['resultsSize'] < len(data['data']['propertySearch']['properties']):
            hotels = []
            for i_hotel in data['data']['propertySearch']['properties'][-user_data["resultsSize"]:]:
                if i_hotel["price"]['lead']['amount'] != 0:
                    price_one_night = get_course_currency(i_hotel["price"]['lead']['amount'], 'USD', user_data['currency'])
                else:
                    price_one_night = 0
                hotel = {'id hotel': i_hotel["id"],
                         'name': i_hotel['name'],
                         'price_one_night': price_one_night}
                hotels.append(hotel)
            hotels.reverse()
            return hotels