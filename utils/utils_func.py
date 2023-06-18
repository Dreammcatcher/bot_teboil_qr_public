import binascii
import configparser
import hashlib
import os
import random
from io import BytesIO
import requests
import xmltodict
from models.model import session, Teboil, UserId
import qrcode
from PIL import Image, ImageDraw, ImageFont
import datetime
from config.config_bot import proxy


def shifr(stroka: str) -> str:
    dk = hashlib.pbkdf2_hmac(hash_name='sha256',
                             # password=b'bad_password',
                             password=bytes(str(stroka), encoding='utf-8'),
                             #salt=b'bad_salt',
                             salt=b'105_bad_salt',
                             #iterations=10000)
                             iterations=2000)
    return str(binascii.hexlify(dk))[2:34]


def generate_codes():
    """
    Генерирует и заполняет в БД столбец кода по id номеру карты
    """
    karts = session.query(Teboil.num_kart).all()
    col = 0
    for i in karts:
        col += 1
        id_kart = session.query(Teboil.id).filter_by(num_kart=i[0]).first()
        if int(id_kart[0]) > 0:
            code = shifr(i[0]) + f'_{id_kart[0]}'
            session.query(Teboil).filter_by(num_kart=i[0]).update({'code': code})
            # if col == 20:
            #     break

            if col % 1000 == 0:
                #print(code)
                print(col)
    session.commit()


#generate_codes()


def generate_codes_from_date():
    """
    Генерирует и заполняет столб кода по текущей дате
    """
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    karts = session.query(Teboil.num_kart).all()
    col = 0
    for i in karts:
        col += 1
        id_kart = session.query(Teboil.id).filter_by(num_kart=i[0]).first()
        code = shifr(date + str(i[0])) + f'_{id_kart[0]}'
        session.query(Teboil).filter_by(num_kart=i[0]).update({'code': code})
        # if col == 100:
        #     break
        if col % 500 == 0:
            print(col)

    session.commit()


#generate_codes_from_date()


# заполнение БД
def zapoln_bd():
    #with open('db_30.01.2023_teboil.txt', 'r', encoding='utf-8') as db:
    with open('базы/db_big_update2.txt', 'r', encoding='utf-8') as db:
        a = db.readlines()
        col, count = 0, 0
        data = None
        for i in a:
            line = i.rstrip().split(':')
            if len(line) == 7:
                data = Teboil(email_osnovnoi=line[0],
                              telefon=int(line[1]),
                              num_kart=int(line[2]),
                              email_new_in_profil=line[3],
                              password_email=line[4],
                              password_account=line[5],
                              token=line[6],
                              )
            elif len(line) >= 8:
                if line[7] == 'False':
                    line[7] = 0

                data = Teboil(email_osnovnoi=line[0],
                              telefon=int(line[1]),
                              num_kart=int(line[2]),
                              email_new_in_profil=line[3],
                              password_email=line[4],
                              password_account=line[5],
                              token=line[6],
                              balans=int(line[7]),
                              )
            col += 1
            if col % 1000 == 0:
                print(col)
            session.add(data)
        print(col)
        session.commit()


#zapoln_bd()


async def create_qr_after_update(nomer, name_lvl, balance):
    """
    :param name_lvl -> Agate | Sapphire | Ruby | Diamond
    :return объект собранной картинки карты лояльности
    """
    qrimg = qrcode.make(nomer)
    img = None
    if name_lvl == 'Agate':
        img = Image.open('images/without_qr_new_logo_agate.png')
    # elif name_lvl == 'Sapphire':
    #     img = Image.open('images/teboil_sapphire.png')
    # elif name_lvl == 'Ruby':
    #     img = Image.open('images/teboil_ruby.png')
    # elif name_lvl == 'Diamond':
    #     img = Image.open('images/teboil_diamond.png')

    font = ImageFont.truetype("images/Hakuna-Sans.otf", 60)
    drawer = ImageDraw.Draw(img)
    if int(balance) > 999:
        drawer.text((330, 524), str(balance), font=font, fill='white', stroke_width=0)
    else:
        drawer.text((360, 524), str(balance), font=font, fill='white', stroke_width=0)

    width, height = qrimg.size
    barcod = qrimg.crop((37, 37, width - 37, height - 37))

    qrimg = barcod.resize((665, 665))
    imag1 = img.copy()
    imag1.paste(qrimg, (202, 768))
    #imag1.save('ready.png', quality=100)
    image_kart_buffer = BytesIO()
    image_kart_buffer.name = 'ready.png'
    imag1.save(image_kart_buffer, 'png')
    image_kart_buffer.seek(0)
    return image_kart_buffer


def response_to_teboil(token: str) -> requests:
    headers = {
        'Host': 'loy.teboil-azs.ru',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',  # забанили его
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.75 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://loy.teboil-azs.ru/profile',
        'Origin': 'https://loy.teboil-azs.ru',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Authorization': 'Bearer ' + token,
    }
    response = requests.get('https://loy.teboil-azs.ru/api/v1/profile', headers=headers, proxies=proxy, timeout=50)
    return response


def responce_to_teboil_after_update(card_number: any) -> tuple[str, str, str]:
    """
    лвл карты -> Agate | Ruby | Sapphire | Diamond
    :returns лвл карты, баланс, литры
    """

    headers = {
        'Host': 'ws-4ghj23.teboil-azs.ru',
        'User-Agent': 'Dart/2.18 (dart:io)',
        'content-type': 'text/xml;charset=UTF-8',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    data = f'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:per="https://licard.ru/interation/PersonalAccount">\n  <soapenv:Header/>\n  <soapenv:Body>\n    <per:GetSessionIdByCardNumber>\n      <per:CardNumber>{int(card_number)}</per:CardNumber>\n    </per:GetSessionIdByCardNumber>\n  </soapenv:Body>\n</soapenv:Envelope>'
    response = requests.post('https://ws-4ghj23.teboil-azs.ru/esb/v1', headers=headers, data=data, proxies=proxy)
    data_dict = xmltodict.parse(response.text)
    sesion_id = data_dict['soapenv:Envelope']['S:Body']['tns:GetSessionIdByCardNumberResponse']['tns:SessionId']

    data2 = f'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:per="https://licard.ru/interation/PersonalAccount">\n  <soapenv:Header/>\n  <soapenv:Body>\n    <per:LoginAndGetClientInfo>\n      <per:Source>ЛК</per:Source>\n      <per:SessionAuth>\n        <per:Login>{card_number}</per:Login>\n        <per:SessionId>{sesion_id}</per:SessionId>\n      </per:SessionAuth>\n    </per:LoginAndGetClientInfo>\n  </soapenv:Body>\n</soapenv:Envelope>'.encode()
    response2 = requests.post('https://ws-4ghj23.teboil-azs.ru/esb/v1', headers=headers, data=data2, proxies=proxy)
    data_dict = xmltodict.parse(response2.text)
    card_info = data_dict['soapenv:Envelope']['SOAP-ENV:Body']['tns:LoginAndGetClientInfoResponse']['tns:ClientInfo']['tns:Cards']['tns:Card']

    balance: str = card_info['tns:CardBalance']
    kart_lvl: str = card_info['tns:CurrentTierCode']

    Qual_fuel: str = card_info['tns:Qual_Fuel2']    # литры топлива
    #Qual_nonfuel: str = card_info['tns:Qual_NonFuel3']   # товары

    # print(balance)
    # print(kart_lvl)
    # print(Qual_fuel)
    # print(Qual_nonfuel)
    return kart_lvl, balance, Qual_fuel


# def response_to_yandex() -> requests:
#     response = requests.get('https://ya.ru', proxies=proxy, timeout=30)
#     return response


def check_odinakov_karts():
    bd = session.query(Teboil.num_kart).all()
    col = 0
    for i in range(len(bd)):
        col += 1
        numer = bd[i]
        for j in range(len(bd)):
            if numer == bd[j] and i != j:
                print(f'{numer} {i} {j}')
        if col % 500 == 0:
            print(f'проверено ---  {col} карт')
    #print(f'всего одинаковых карт ----{odin}')


#check_odinakov_karts()

def read_file_id():
    with open('all_id.txt', 'r') as f:
        lis = f.readlines()
        for k in lis:
            k = k.split(':')
            data = UserId(user_id=int(k[0]),
                          user_name=k[1].rstrip())
            session.add(data)
        session.commit()


#read_file_id()


def append_user_to_bd(user_id: any, user_name: str):
    data = UserId(user_id=int(user_id),
                  user_name=user_name)
    session.add(data)
    session.commit()


# заполнение БД 105 к
def zapoln_bd_105():
    #with open('db_30.01.2023_teboil.txt', 'r', encoding='utf-8') as db:
    with open('базы/teboil_mydb_balance_card-105.txt', 'r', encoding='utf-8') as db:
        a = db.readlines()
        col, count = 0, 0
        data = None
        for i in a:
            line = i.rstrip().split(':')
            if line[3] == '':
                tel = None
            else:
                tel = int(line[3])
            try:
                data = Teboil(num_kart=int(line[0]),
                              balans=int(line[1]),
                              lvl_card=line[2],
                              telefon=tel,
                              #
                              email_osnovnoi=line[5],
                              )
            except IndexError:
                data = Teboil(num_kart=int(line[0]),
                               balans=int(line[1]),
                               lvl_card=line[2],
                               telefon=tel,
                               #
                               email_osnovnoi=None,
                               )
            col += 1
            if col % 5000 == 0:
                print(col)
            session.add(data)
        print(col)
        session.commit()


#zapoln_bd_105()

def more_than(sp: list):
    """
    :returns lvl_kart, balance
    """
    if '>' in sp:
        nominal = int(sp[2])
        try:
            data = session.query(Teboil.lvl_card, Teboil.balans).filter(Teboil.balans > nominal).filter(Teboil.balans < nominal+100).all()
            random_karts = random.choice(data)
        except Exception:
            return False
        else:
            return random_karts[0], random_karts[1]
    else:
        return None


#more_than(['/bot_give_me_qr', '>', '500'])
