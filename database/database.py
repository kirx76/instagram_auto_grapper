import datetime
import os

from dotenv import load_dotenv
from peewee import *

from misc import dbm

load_dotenv()

PEEWEE_DB_PATH = os.environ.get("PEEWEE_DB_PATH")

db = SqliteDatabase(PEEWEE_DB_PATH)


def initialize_db():
    dbm('Connecting to database')
    db.connect()
    dbm('Creating tables or initialization tables')
    db.create_tables(
        [TelegramUser, InstagramAccount, InstagramSubscription, InstagramPost, InstagramHighlight, InstagramStory])
    db.close()
    dbm('Database initialization complete')


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(PEEWEE_DB_PATH)

    def save_if_not_exists(self):
        self.save()
        pass


class TelegramUser(BaseModel):
    username = CharField()
    user_id = CharField(unique=True)
    first_join = DateTimeField(default=datetime.datetime.now)
    last_action_time = DateTimeField(default=datetime.datetime.now)
    selected_instagram_account = CharField(null=True)
    selected_instagram_subscription = CharField(null=True)

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

    def save(self, *args, **kwargs):
        self.last_iteration_at = datetime.datetime.now()
        return super(InstagramAccount, self).save(*args, **kwargs)


class InstagramSubscription(BaseModel):
    username = CharField()
    enabled = BooleanField(default=False)
    added_by = ForeignKeyField(TelegramUser, backref='instagram_subscriptions')


class InstagramPost(BaseModel):
    owner = ForeignKeyField(InstagramSubscription, backref='posts')
    pk = CharField(unique=True)
    taken_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    caption_text = TextField(null=True)


class InstagramStory(BaseModel):
    owner = ForeignKeyField(InstagramSubscription, backref='stories')
    pk = CharField(unique=True)
    taken_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    caption_text = TextField(null=True)


class InstagramHighlight(BaseModel):
    owner = ForeignKeyField(InstagramSubscription, backref='highlights')
    pk = CharField(unique=True)
    taken_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)
    caption_text = TextField(null=True)


def create_db_telegram_user(username, user_id):
    user, created = TelegramUser.get_or_create(username=username, user_id=user_id)
    if created:
        dbm(f'User {username} created')
    else:
        dbm(f'User {username} already exists')
    return user


def get_current_telegram_user(user_id):
    dbm('Getting current telegram user')
    return TelegramUser.select().where(TelegramUser.user_id == user_id).first()


def get_telegram_user_instagram_accounts(user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram accounts')
    return InstagramAccount.select().where(InstagramAccount.added_by == telegram_user.id).execute()


def get_selected_instagram_account(user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user selected instagram account')
    return InstagramAccount.select().where(
        (InstagramAccount.username == telegram_user.selected_instagram_account) & (
                InstagramAccount.added_by == telegram_user.id)).first()


def get_selected_instagram_subscription(user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user selected instagram subscription')
    return InstagramSubscription.select().where(
        (InstagramSubscription.username == telegram_user.selected_instagram_subscription) & (
                InstagramSubscription.added_by == telegram_user.id)).first()


def set_selected_instagram_account_validity(user_id, state):
    ia = get_selected_instagram_account(user_id)
    dbm('Change selected instagram account validity')
    ia.is_valid = state
    ia.last_validation_at = datetime.datetime.now()
    ia.save()
    return ia


def toggle_selected_active_instagram_account(user_id):
    ias = get_telegram_user_instagram_accounts(user_id)
    dbm('Toggled selected instagram account activity')
    for ia in ias:
        ia.is_active = False
        ia.save()
    ia = get_selected_instagram_account(user_id)
    ia.is_active = False if ia.is_active else True
    ia.save()
    return ia


def toggle_selected_active_instagram_subscription(user_id):
    isub = get_selected_instagram_subscription(user_id)
    dbm('Toggled selected instagram subscription activity')
    isub.enabled = False if isub.enabled else True
    isub.save()
    return isub


def select_instagram_account(username, user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Selecting instagram account')
    telegram_user.selected_instagram_account = username
    telegram_user.save()
    return get_selected_instagram_account(user_id)


def select_instagram_subscription(username, user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Selecting instagram subscription')
    telegram_user.selected_instagram_subscription = username
    telegram_user.save()
    return get_selected_instagram_subscription(user_id)


def add_instagram_account(username, password, user_id):
    telegram_user = get_current_telegram_user(user_id)
    ia, created = InstagramAccount.get_or_create(username=username, password=password, added_by=telegram_user.id)
    if created:
        dbm(f'Instagram account {username} created')
    else:
        dbm(f'Instagram account {username} already exists')
    return ia


def add_instagram_subscription(username, user_id):
    telegram_user = get_current_telegram_user(user_id)
    isub, created = InstagramSubscription.get_or_create(username=username, added_by=telegram_user.id)
    if created:
        dbm(f'Instagram subscription {username} added by {telegram_user.username}')
    else:
        dbm(f'Instagram subscription {username} for {telegram_user.username} already exists')
    return isub


def get_instagram_accounts_by_telegram_user_id(user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram accounts')
    return InstagramAccount.select(InstagramAccount.username).where(
        InstagramAccount.added_by == telegram_user.id).execute()


def get_telegram_user_instagram_subscriptions(user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram subscriptions')
    return InstagramSubscription.select().where(InstagramSubscription.added_by == telegram_user.id).execute()


def get_telegram_user_active_instagram_account(user_id):
    telegram_user = get_current_telegram_user(user_id)
    return InstagramAccount.select().where(
        (InstagramAccount.added_by == telegram_user.id) & (InstagramAccount.is_active == True)).first()


def add_instagram_post_to_instagram_subscription(owner, pk, caption_text, taken_at):
    return InstagramPost(owner=owner, pk=pk, caption_text=caption_text, taken_at=taken_at).save()


def add_instagram_story_to_instagram_subscription(owner, pk, caption_text, taken_at):
    return InstagramStory(owner=owner, pk=pk, caption_text=caption_text, taken_at=taken_at).save()


def add_instagram_highlight_to_instagram_subscription(owner, pk, caption_text, taken_at):
    return InstagramHighlight(owner=owner, pk=pk, caption_text=caption_text, taken_at=taken_at).save()

