from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session


Base = declarative_base()


class Teboil(Base):
    __tablename__ = 'db_teboil-105_v1.1'
    id = Column(Integer, primary_key=True)
    email_osnovnoi = Column(String, default=None)
    telefon = Column(Integer, default=None)
    num_kart = Column(Integer, default=None)
    email_new_in_profil = Column(String, default=None)
    password_email = Column(String, default=None)
    password_account = Column(String, default=None)
    token = Column(String, default=None)
    balans = Column(Integer, default=None)
    code = Column(String, default=None)
    status_sell = Column(String, default=None)
    lvl_card = Column(String, default=None)


class UserId(Base):
    __tablename__ = 'db_user_id_v1.0'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, default=None)
    user_name = Column(String, default=None)


#engine = create_engine('sqlite:///c:/pythonProject/pivto4ka/db.sqlite3', echo=False, connect_args={'timeout': 100})
engine = create_engine('sqlite:///.../pivto4ka/db.sqlite3', echo=False, connect_args={'timeout': 100})
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(bind=engine))
