import configparser
import os
from logging.handlers import RotatingFileHandler
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

if not os.path.exists('logs'):
    os.makedirs('logs')


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8',
                    handlers=[RotatingFileHandler('./logs/bot_logs.log', maxBytes=150000, backupCount=10)])


# logging.disable(logging.WARNING)

conf = configparser.ConfigParser()
if os.path.isfile('./venv/config.ini'):
    conf.read('./venv/config.ini', encoding='utf-8')
else:
    conf.read('config.ini', encoding='utf-8')

bot_token = conf['VARIABLES']['bot_token']
url = conf['VARIABLES']['url']
login_prox = conf['VARIABLES']['login']
password_prox = conf['VARIABLES']['password']
change_api = conf['VARIABLES']['change_api']
admin_id: list[str] = conf['VARIABLES']['admin_id'].split(',')
time_del_kart = conf['VARIABLES']['time_del_kart']
proxy = {'https': f'http://{login_prox}:{password_prox}@{url}'}


bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
