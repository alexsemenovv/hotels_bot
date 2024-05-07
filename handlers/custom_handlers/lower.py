from __future__ import annotations

from utils.utils import *


@logger.catch
def get_id_hotels(user_data) -> List | None:
    """
    :param data: Словарь с валютой, id локации из city_founding, дата заезда, дата выезда, взрослые, дети
    :return: Список отелей с ценой за одну ночь, id и имя
    """
    logger.info(f"custom handlers.lower.get_id_hotels params: {user_data}")
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
               'resultsSize': user_data['resultsSize'],
               'sort': 'PRICE_LOW_TO_HIGH',
               'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
               }

    if user_data['count children'] is None:
        logger.info(f"custom handlers.lower.get_id_hotels - data without children")
        payload['rooms'] = [{'adults': user_data['adults']}]
    else:
        logger.info(f"custom handlers.lower.get_id_hotels - data with {user_data['children']} children")
        payload['rooms'] = [{'adults': 1, 'children': user_data['children']}]
    response = api_request(url, payload, 'POST')
    if response:
        logger.info(f"custom handlers.lower.get_id_hotels - get response {response}")
        data = json.loads(response)
        if 'errors' in data:
            logger.error(f'custom handlers.lower.get_id_hotels: нет данных по заданным параметрам - {data}')
            return 'Ошибка'
        hotels = list()

        for i_hotel in data['data']['propertySearch']['properties']:
            price_one_night = get_course_currency(i_hotel["price"]['lead']['amount'], 'USD', user_data['currency'])
            hotel = {'id hotel': i_hotel["id"],
                     'name': i_hotel['name'],
                     'price_one_night': price_one_night}
            hotels.append(hotel)
        return hotels
    return response
