from __future__ import annotations
import requests
from config_data.config import RAPID_API_KEY
from loguru import logger
import datetime


logger.add(f'logs/debug.{datetime.datetime.now().date()}.log',
           format="{time} {level} {message}",
           level='DEBUG', rotation='10 MB', compression='zip') # Добавление логгера, который создаёт лог файл каждый день

@logger.catch
def api_request(method_endswith: str, params: dict[str, str], method_type: str) -> str | None:
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    logger.info(f"request_to_api.request.api_request - method_endswith: {method_endswith}, params: {params}, method_type: {method_type}")
    if method_type == 'GET':
        return get_request(
            url=url,
            params=params
        )
    else:
        return post_request(
            url=url,
            params=params
        )


@logger.catch
def get_request(url, params) -> str | None:
    try:
        logger.info(f"request_to_api.request.get_request - url: {url}, params: {params}")
        response = requests.get(
            url,
            headers={
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
},
            params=params,
            timeout=15
        )
        if response.status_code == requests.codes.ok:
            logger.info(f"request_to_api.request.get_request - status: {response.status_code}")
            return response.text
    except requests.ConnectionError as connect_error:
        logger.error(f"request_to_api.request.get_request - error: {connect_error}")
        return None
    except requests.ReadTimeout as timeout_error:
        logger.error(f"request_to_api.request.get_request - error: {timeout_error}")
        return None


@logger.catch
def post_request(url, params) -> str | None:
    try:
        logger.info(f"request_to_api.request.post_request - url: {url}, params: {params}")
        response = requests.request(
            'POST',
            url,
            json=params,
            headers={
                "X-RapidAPI-Key": RAPID_API_KEY,
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            timeout=15
                                    )
        if response.status_code == requests.codes.ok:
            logger.info(f"request_to_api.request.post_request - status: {response.status_code}")
            return response.text
    except requests.ConnectionError as connect_error:
        logger.error(f"request_to_api.request.post_request - error: {connect_error}")
        return None
    except requests.exceptions.ReadTimeout as timeout_error:
        logger.error(f"request_to_api.request.post_request - error: {timeout_error}")
        return None

