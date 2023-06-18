import binascii
import datetime
import hashlib
import time

from models.model import session, Teboil


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


def update_balance():
    with open('tb_acc_recheck_dublicate.txt', 'r') as f:
        data = [x.rstrip() for x in f.readlines()]
    for i in data:
        i = i.split(':')
        num_kart = i[1]
        type_kart = i[2]
        balance = i[3]
        session.query(Teboil).filter_by(num_kart=int(num_kart)).update({'lvl_card': type_kart, 'balans': balance})
    session.commit()


#update_balance()
