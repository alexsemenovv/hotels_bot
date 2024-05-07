from dotenv import find_dotenv, load_dotenv
import os

if not find_dotenv():
    exit('Переменные окружения не загружены т.к. отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('low', 'Запросить дешевые отели'),
    ('high', 'Запрсить дорогие отели'),
    ('custom', 'Ручной запрос'),
    ('history', 'История запросов')
)



