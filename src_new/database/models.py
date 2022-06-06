import datetime
import os

from dotenv import load_dotenv
from peewee import *

from database.misc import get_db

load_dotenv()

PG_APP_NAME = os.environ.get("PG_APP_NAME")
PG_USER = os.environ.get("PG_USER")
PG_USER_PASSWORD = os.environ.get("PG_USER_PASSWORD")
PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT")
DEBUG = os.environ.get("DEBUG")

db = get_db()


class BaseModel(Model):
    class Meta:
        database = db


class TUserStatus(BaseModel):
    name = CharField()


class TUser(BaseModel):
    username = CharField()
    user_id = CharField(unique=True)
    first_join = DateTimeField(default=datetime.datetime.now)
    status = ForeignKeyField(TUserStatus, backref='user_status', default=1)


class IAccount(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    owner = ForeignKeyField(TUser, backref='i_accounts')
    dump_data = TextField(null=True)


class IUser(BaseModel):
    pk = TextField(unique=True, primary_key=True)
    username = TextField(unique=True)
    full_name = TextField(null=True)
    profile_pic_url = TextField(null=True)
    profile_pic_url_hd = TextField(null=True)
    is_private = CharField(null=True)
    enabled = BooleanField(default=False)
    added_by = ForeignKeyField(TUser, backref='i_users')
    telegram_file_id = TextField(null=True)
    available_for = ManyToManyField(TUser, 'i_users')
    added_at = DateTimeField(default=datetime.datetime.now)


TUserIUsers = IUser.available_for.get_through_model()


class IPost(BaseModel):
    pk = CharField(unique=True)
    code = TextField()
    taken_at = DateTimeField()
    # media_type = IntegerField()
    # thumbnail_url = TextField(null=True)
    user = ForeignKeyField(IUser, backref='posts')
    caption_text = TextField(null=True)
    telegram_file_id = TextField(null=True)


class IStory(BaseModel):
    pk = CharField(unique=True)
    code = TextField()
    taken_at = DateTimeField()
    # media_type = IntegerField()
    # thumbnail_url = TextField(null=True)
    # video_url = TextField(null=True)
    # video_duration = FloatField(null=True)
    user = ForeignKeyField(IUser, backref='stories')
    caption_text = TextField(null=True)
    telegram_file_id = TextField(null=True)


class IPostResource(BaseModel):
    pk = CharField(unique=True, primary_key=True)
    # video_url = TextField(null=True)
    # thumbnail_url = TextField(null=True)
    # media_type = IntegerField()
    post = ForeignKeyField(IPost, backref='resources')
    telegram_file_id = TextField(null=True)
