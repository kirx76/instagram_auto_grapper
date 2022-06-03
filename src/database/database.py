import datetime
import os

from dotenv import load_dotenv
from peewee import *
from playhouse.migrate import PostgresqlMigrator, migrate
from playhouse.postgres_ext import PostgresqlExtDatabase

from utils.misc import dbm

load_dotenv()

PG_APP_NAME = os.environ.get("PG_APP_NAME")
PG_USER = os.environ.get("PG_USER")
PG_USER_PASSWORD = os.environ.get("PG_USER_PASSWORD")
PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT")
DEBUG = os.environ.get("DEBUG")

if DEBUG == 'True':
    db = SqliteDatabase('debug.db')
else:
    db = PostgresqlExtDatabase(PG_APP_NAME, user=PG_USER, password=PG_USER_PASSWORD, host=PG_HOST, port=PG_PORT,
                           autocommit=True,
                           thread_safe=True)

# migrator = PostgresqlMigrator(db)
# telegram_file_id = TextField(null=True)


def initialize_db():
    dbm('PIZDA')
    dbm('Connecting to database')
    db.connect()
    dbm('Creating tables or initialization tables')
    db.create_tables(
        [TelegramUser, TelegramUserStatus, InstagramUser,
         InstagramAccount, InstagramPost, InstagramPostResource,
         InstagramHighlight, InstagramStory, TelegramUserInstagramUsers])
    db.close()
    initialize_user_statuses()
    dbm('Database initialization complete')


def initialize_user_statuses():
    dbm('Initializing user statuses')
    TelegramUserStatus.get_or_create(name='Usual')
    TelegramUserStatus.get_or_create(name='Normal')
    TelegramUserStatus.get_or_create(name='Banned')
    TelegramUserStatus.get_or_create(name='VIP')
    TelegramUserStatus.get_or_create(name='Admin')
    dbm('Initializing user statuses complete')


class BaseModel(Model):
    class Meta:
        database = db

    def save_if_not_exists(self):
        self.save()
        pass


class TelegramUserStatus(BaseModel):
    name = CharField()


class TelegramUser(BaseModel):
    username = CharField()
    user_id = CharField(unique=True)
    first_join = DateTimeField(default=datetime.datetime.now)
    last_action_time = DateTimeField(default=datetime.datetime.now)
    selected_instagram_account = CharField(null=True)
    selected_instagram_user = CharField(null=True)
    status = ForeignKeyField(TelegramUserStatus, backref='user_status', default=1)

    # TODO ADD DOWNLOADING STATUS FOR THREAD (TO OFF DOWNLOADS IF NOT NEEDED)
    # downloading_enabled = BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.last_action_time = datetime.datetime.now()
        return super(TelegramUser, self).save(*args, **kwargs)


class InstagramAccount(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    verification_code = CharField(max_length=6, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=False)
    last_iteration_at = DateTimeField(null=True)
    added_by = ForeignKeyField(TelegramUser, backref='instagram_accounts')
    is_valid = BooleanField(default=False)
    last_validation_at = DateTimeField(default=datetime.datetime.now)
    downloading_now = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    dump_data = TextField(null=True)

    def save(self, *args, **kwargs):
        self.last_iteration_at = datetime.datetime.now()
        return super(InstagramAccount, self).save(*args, **kwargs)


class InstagramUser(BaseModel):
    pk = TextField(unique=True, primary_key=True)
    username = TextField(unique=True)
    full_name = TextField(null=True)
    profile_pic_url = TextField(null=True)
    profile_pic_url_hd = TextField(null=True)
    is_private = CharField(null=True)
    enabled = BooleanField(default=False)
    added_by = ForeignKeyField(TelegramUser, backref='instagram_users')
    profile_pic_location = TextField(null=True)
    available_for = ManyToManyField(TelegramUser, 'instagram_users')
    added_at = DateTimeField(default=datetime.datetime.now)


TelegramUserInstagramUsers = InstagramUser.available_for.get_through_model()


class InstagramPost(BaseModel):
    pk = CharField(unique=True)
    code = TextField()
    taken_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    media_type = IntegerField()
    thumbnail_url = TextField(null=True)
    user = ForeignKeyField(InstagramUser, backref='posts')
    caption_text = TextField(null=True)
    telegram_file_id = TextField(null=True)


class InstagramStory(BaseModel):
    pk = CharField(unique=True)
    code = TextField()
    taken_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    media_type = IntegerField()
    thumbnail_url = TextField(null=True)
    video_url = TextField(null=True)
    video_duration = FloatField(null=True)
    user = ForeignKeyField(InstagramUser, backref='stories')
    caption_text = TextField(null=True)
    telegram_file_id = TextField(null=True)


class InstagramHighlight(BaseModel):
    pk = CharField(unique=True)
    code = TextField()
    taken_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    media_type = IntegerField()
    thumbnail_url = TextField(null=True)
    video_url = TextField(null=True)
    video_duration = FloatField(null=True)
    user = ForeignKeyField(InstagramUser, backref='highlights')
    caption_text = TextField(null=True)
    telegram_file_id = TextField(null=True)


class InstagramPostResource(BaseModel):
    pk = CharField(unique=True, primary_key=True)
    video_url = TextField(null=True)
    thumbnail_url = TextField(null=True)
    media_type = IntegerField()
    post = ForeignKeyField(InstagramPost, backref='resources')
    telegram_file_id = TextField(null=True)

# migrate(
#     migrator.add_column('instagrampost', 'telegram_file_id', telegram_file_id),
#     migrator.add_column('instagramstory', 'telegram_file_id', telegram_file_id),
#     migrator.add_column('instagramhighlight', 'telegram_file_id', telegram_file_id),
#     migrator.add_column('instagrampostresource', 'telegram_file_id', telegram_file_id),
# )
