import time

from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from config.config_bot import bot, logging
from config.states import UserState
from models.model import session, UserId, Teboil
from io import BytesIO, StringIO


blacklist_name = dict()
count_bad_enter = dict()


async def start(message: types.Message):
    await bot.send_message(message.chat.id, '🚘 Привет, введи приобретённый код активации...', reply_markup=ReplyKeyboardRemove())
    await UserState.enter.set()


async def give_logs(message: types.Message):
    user_name1 = message.from_user
    await bot.send_message(message.chat.id, '⚠️ Выгружаю файл с логами...')
    logging.info(f'Выгружен файл с логами, пользователь - {user_name1}')
    await bot.send_document(message.chat.id, open('./logs/bot_logs.log', 'rb'))
    await UserState.enter.set()


async def give_blacklist(message: types.Message):
    user_name = message.from_user
    await bot.send_message(message.chat.id, '⚠️ Выгружаю blacklist...')
    logging.info(f'Выгружен blacklist, пользователь - {user_name}\n')
    await bot.send_message(message.chat.id, f'{blacklist_name}')
    await UserState.enter.set()


async def clear_blacklist(message: types.Message):
    user_name = message.from_user
    blacklist_name.clear()
    count_bad_enter.clear()
    logging.info(f'Blacklist очищен, пользователь - {user_name}\n')
    await bot.send_message(message.chat.id, '⚠️ Blacklist очищен')
    await UserState.enter.set()


async def append_user_to_blacklicst(message: types.Message):
    await bot.send_message(message.chat.id, 'Введи имя юзера или id:')
    await UserState.append_user.set()


async def append_user(message: types.Message):
    if message.text.isdigit():
        blacklist_name.setdefault(int(message.text), None)
    else:
        blacklist_name.setdefault(None, message.text)
    logging.info(f'Пользователь {message.text} добавлен в черный список\n')
    await bot.send_message(message.chat.id, f'⚠️ Пользователь {message.text} добавлен в blacklist')
    await bot.send_message(message.chat.id, f'Текущий blacklist-\n{blacklist_name}')
    await UserState.enter.set()


async def send_message(message: types.Message):
    text_message = message.text[18:]
    await bot.send_message(message.chat.id, 'Начинаю отправку сообщения...')
    all_data = session.query(UserId.user_id, UserId.user_name).all()
    col = 0
    for j in all_data:
        ids = j[0]
        name = j[1]
        try:
            await bot.send_message(ids, text_message)
            col += 1
        except Exception as er:
            logging.info(f'Ошибка рассылки, пользователь - {ids} {name}, ошибка {er}')
            continue
    await bot.send_message(message.chat.id, f'Рассылка закончена, всего оповещено {col} пользователей')
    logging.info(f'Проведена рассылка с сообщением-{text_message}')
    await UserState.enter.set()


async def delete_status_sell(message: types.Message):
    mes = message.text.split()
    if len(mes) != 2:
        await bot.send_message(message.chat.id, "Не надо просто кликать, допиши хеш-код или телефон")
        await UserState.enter.set()
    else:
        code_hash = mes[1]
        if len(code_hash) == 16:
            status = session.query(Teboil.status_sell).filter_by(num_kart=code_hash).first()
        else:
            status = session.query(Teboil.status_sell).filter_by(code=code_hash).first()
        if status is not None:
            if status[0] is not None:
                session.query(Teboil).filter_by(num_kart=code_hash).update({'status_sell': None})
                session.query(Teboil).filter_by(code=code_hash).update({'status_sell': None})
                session.commit()
                await bot.send_message(message.chat.id, f"Статус продажи кода - {code_hash} сброшен")
            else:
                await bot.send_message(message.chat.id, "Данный код еще не продан")
        else:
            await bot.send_message(message.chat.id, "Данный код отсутствует в БД")
        await UserState.enter.set()


async def readme(message: types.Message):
    await bot.send_message(message.chat.id, '/bot_give_me_logs  - выгрузка текущего каталога логов в чат\n'
                                            '/bot_give_me_blacklist  - получение черного списка в чат\n'
                                            '/bot_clear_blacklist  - очищение черного списка\n'
                                            '/bot_send_message <текст> - рассылка текста всем пользователям бота\n'
                                            '/append_user_to_blacklicst - добавление пользователя в черный список\n'
                                            '/delete_status_sell <hash code или тел> - удаление статуса "SOLD" в БД\n'
                                            'номер телефона в формате 79115553322\n'
                                            '/bot_give_me_number_sold - выдает коды проданных карт в файле\n'
                                            '/give_me_qrcode <сумма> - выдает qrcode приближенный к этой сумме +-50')
    await UserState.enter.set()


async def bot_give_me_number_sold(message: types.Message):
    data = session.query(Teboil.code).filter_by(status_sell='SOLD').all()
    await bot.send_message(message.chat.id, '⚠️ Выгружаю файл с кодами...')
    strin = StringIO()
    for i in data:
        st = i[0]
        strin.write(st + '\n')
    await bot.send_document(message.chat.id, ('sold_karts.txt', StringIO(strin.getvalue())))
    await UserState.enter.set()


async def give_me_qrcode(message: types.Message):
    await bot.send_message(message.chat.id, "Подожди, ищу подходящую карту...")
    mes = message.text.split()
    if len(mes) != 2:
        await bot.send_message(message.chat.id, "Не надо просто кликать, напиши сумму")
        await UserState.enter.set()
    else:
        balance = mes[1]
        dat = session.query(Teboil.balans, Teboil.code).filter_by(status_sell=None).all()
        for i in dat:
            if int(balance) - 50 < i[0] < int(balance) + 50:
                resp = get_info_user(i[1], ip)
                qr_user = resp.json()['QRcode']
                resp_balance = resp.json()['CurrentBonus']
                session.query(Teboil).filter_by(token=i[1]).update({'qrcode': qr_user,
                                                                   'type_kart': resp.json()['BonusStatus']['Title'],
                                                                   'balance': resp_balance,
                                                                   'curent_sum': resp.json()['CurrentSum']})
                session.commit()
                if int(balance) - 50 < int(resp_balance) < int(balance) + 50:
                    image_qr = create_qr_bushe(qr_user)
                    await bot.send_message(message.chat.id, 'Подходящая карта найдена')
                    await bot.send_message(message.chat.id, '👉Загружается QR...\n')
                    await bot.send_photo(message.chat.id, photo=image_qr)
                    await bot.send_message(message.chat.id, f'🟩 Баллы на карте - {resp_balance}\n')
                    hash_code = i[2]
                    await bot.send_message(message.chat.id, f'После использования сними с продажи карту - {hash_code}')
                    user_name = message.from_user.username
                    logging.info(f'Выдана карта админу - {hash_code}, баланс - {resp_balance}, пользователь - {user_name}\n')
                    session.query(Bushe).filter_by(code=hash_code).update({'status_sell': 'SOLD',
                                                                           'balance': resp_balance,
                                                                           'qrcode': qr_user})
                    session.commit()
                    break
                else:
                    time.sleep(2)
                    continue

