import datetime
import os

from dotenv import load_dotenv
from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase


load_dotenv()

PG_APP_NAME = os.environ.get("PG_APP_NAME")
PG_USER = os.environ.get("PG_USER")
PG_USER_PASSWORD = os.environ.get("PG_USER_PASSWORD")
PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT")
DEBUG = os.environ.get("DEBUG")






if __name__ == '__main__':
    if DEBUG == 'True':
        db = SqliteDatabase('debug.db')
    else:
        db = PostgresqlExtDatabase(PG_APP_NAME, user=PG_USER, password=PG_USER_PASSWORD, host=PG_HOST, port=PG_PORT,
                           autocommit=True,
                           thread_safe=True)


    class BaseModel(Model):
        class Meta:
            database = db

    class TUser(BaseModel):
        username = CharField()
        id = IntegerField(unique=True, primary_key=True)


    class IAccount(BaseModel):
        username = CharField(unique=True)
        password = CharField()


    def initialize_database():
        db.connect()
        db.create_tables()
