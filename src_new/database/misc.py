from peewee import *


def get_db():
    return SqliteDatabase('debug.db')
