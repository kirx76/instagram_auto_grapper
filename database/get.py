from database.database import TelegramUser, InstagramAccount, InstagramUser
from utils.misc import dbm


def get_telegram_user_by_instagram_user_username(username) -> TelegramUser:
    dbm('Getting telegram user by instagram user username')
    return TelegramUser.select().join(InstagramUser).where(
        InstagramUser.username == username).first()


def get_active_instagram_account_by_telegram_user_id(user_id) -> InstagramAccount:
    dbm('Getting active instagram account for telegram user')
    return InstagramAccount.select().join(TelegramUser).where(
        (InstagramAccount.is_active == True) & (InstagramAccount.is_valid == True) & (
                TelegramUser.user_id == user_id)).first()


def get_active_instagram_account_by_instagram_user(instagram_user) -> InstagramAccount:
    dbm('Getting active instagram account by instagram user')
    return InstagramAccount.select().join(TelegramUser).join(
        InstagramUser).where(
        (InstagramUser.username == instagram_user.username) & (InstagramAccount.is_active == True) & (
                InstagramAccount.is_valid == True)).first()


def get_all_instagram_accounts_for_admin() -> list[InstagramAccount]:
    dbm('Get all instagram accounts for admin')
    return InstagramAccount.select().execute()


def get_enabled_instagram_users() -> list[InstagramUser]:
    dbm('Getting all enabled instagram users')
    return InstagramUser.select().where(InstagramUser.enabled == True).execute()


def get_telegram_user_active_instagram_account(user_id) -> InstagramAccount:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user active instagram account')
    return InstagramAccount.select().where(
        (InstagramAccount.added_by == telegram_user.id) & (InstagramAccount.is_active == True)).first()


def get_telegram_user_instagram_users(user_id) -> list[InstagramUser]:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram users')
    return InstagramUser.select().where(InstagramUser.added_by == telegram_user.id).execute()


def get_instagram_accounts_by_telegram_user_id(user_id) -> list[InstagramAccount]:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram accounts')
    return InstagramAccount.select(InstagramAccount.username).where(
        (InstagramAccount.added_by == telegram_user.id) & (InstagramAccount.is_deleted == False)).execute()


def select_instagram_user(username, user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Selecting instagram user')
    telegram_user.selected_instagram_user = username
    telegram_user.save()
    return get_selected_instagram_user(user_id)


def select_instagram_account(username, user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Selecting instagram account')
    telegram_user.selected_instagram_account = username
    telegram_user.save()
    return get_selected_instagram_account(user_id)


def get_selected_instagram_user(user_id) -> InstagramUser:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user selected instagram user')
    return InstagramUser.select().where(
        (InstagramUser.username == telegram_user.selected_instagram_user) & (
                InstagramUser.added_by == telegram_user.id)).first()


def get_selected_instagram_account(user_id) -> InstagramAccount:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user selected instagram account')
    return InstagramAccount.select().where(
        (InstagramAccount.username == telegram_user.selected_instagram_account) & (
                InstagramAccount.added_by == telegram_user.id)).first()


def get_current_telegram_user(user_id) -> TelegramUser:
    dbm('Getting current telegram user')
    return TelegramUser.select().where(TelegramUser.user_id == user_id).first()
