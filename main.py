import asyncio
from contextlib import suppress
from aiogram import executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from config.filters import IsAdmin
from models.model import session, Teboil, UserId
from config.states import UserState
from config.config_bot import dp, logging, bot, bot_token, time_del_kart
from utils.utils_func import append_user_to_bd, create_qr_after_update
from handlers.commands import count_bad_enter, blacklist_name, start, give_logs, give_blacklist, clear_blacklist, \
    append_user_to_blacklicst, append_user, send_message, delete_status_sell, readme, \
    bot_give_me_number_sold, give_me_qrcode
import logging


async def enter(message: types.Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    if count_bad_enter.setdefault(user_id, 0) >= 5:
        logging.info(f'Добавлен пользователь {user_id} {user_name} в черный список')
        blacklist_name.setdefault(user_id, user_name)
    if (user_id in blacklist_name) or (user_name in blacklist_name.values()):
        await UserState.enter.set()
    else:
        enters_code = message.text
        user_info = message.from_user
        user_name = message.from_user.username
        user_firstname = message.from_user.first_name
        num_kart = session.query(Teboil.num_kart).filter_by(code=enters_code).first()
        if num_kart is not None:

            # добавление пользователя в бд
            if (int(user_id),) not in session.query(UserId.user_id).all():
                if user_name is None:
                    user_name = user_firstname
                append_user_to_bd(user_id, user_name)

            status_sell = session.query(Teboil.status_sell).filter_by(code=enters_code).first()
            if (status_sell[0]) is None:
                await bot.send_message(message.chat.id, 'Ожидайте идет генерация карты...')
                balance = session.query(Teboil.balans).filter_by(code=enters_code).first()[0]

                logging.info(f'Введен правильный код - {enters_code}, пользователь - {user_info}')
                img_kart = await create_qr_after_update(num_kart[0], balance)

                await bot.send_message(message.chat.id,
                                       '⚠️QR код  будет автоматически удален через - 3 часа\n\n'
                                       '👉Загружается карта лояльности...')
                imag = await bot.send_photo(message.chat.id, photo=img_kart)
                await bot.send_message(message.chat.id, f'🟩 Баллов на карте - {balance}\n')
                session.query(Teboil).filter_by(code=enters_code).update({'status_sell': 'SOLD'})
                session.commit()
                logging.info(f'Выдана карта - {enters_code}, баланс - {balance}, пользователь - {user_info}\n')
                if time_del_kart != '':
                    asyncio.create_task(delete_message(imag, int(time_del_kart)))
            else:
                logging.warning(f'Код уже использован - {enters_code}, пользователь - {user_info}\n')
                await bot.send_message(message.chat.id, '⚠️Код уже использован, обратитесь в поддержку.')
                await UserState.enter.set()
        else:
            logging.warning(f'Код отсутствует в БД - {enters_code}, пользователь - {user_info}\n')
            await bot.send_message(message.chat.id, 'Что-то не то вводите, проверьте еще раз, или обратитесь к продавцу для уточнения.')
            count_bad_enter[message.from_user.id] = count_bad_enter.get(message.from_user.id, 0) + 1
            await UserState.enter.set()


# космическая ф-я для удаления картинки или сообщения
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


# commands.py
dp.register_message_handler(start, commands='start', state='*')
dp.register_message_handler(give_logs, IsAdmin(), commands=['bot_give_me_logs'], state='*')
dp.register_message_handler(give_blacklist, IsAdmin(), commands=['bot_give_me_blacklist'], state='*')
dp.register_message_handler(clear_blacklist, IsAdmin(), commands=['bot_clear_blacklist'], state='*')
dp.register_message_handler(append_user_to_blacklicst, IsAdmin(), commands=['append_user_to_blacklist'], state='*')
dp.register_message_handler(append_user, state=UserState.append_user)
dp.register_message_handler(send_message, IsAdmin(), commands=['bot_send_message'], state='*')
dp.register_message_handler(delete_status_sell, IsAdmin(), commands=['delete_status_sell'], state='*')
dp.register_message_handler(readme, IsAdmin(), commands=['readme'], state='*')
dp.register_message_handler(bot_give_me_number_sold, IsAdmin(), commands=['bot_give_me_number_sold'], state='*')
dp.register_message_handler(give_me_qrcode, IsAdmin(), commands=['give_me_qrcode'], state='*')

# main.py
dp.register_message_handler(enter, state=[UserState.enter, None])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)