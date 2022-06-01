from database.database import TelegramUser, InstagramAccount, InstagramUser, InstagramStory, \
    InstagramHighlight, TelegramUserInstagramUsers, InstagramPost, InstagramPostResource
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


def get_enabled_instagram_users() -> list[InstagramUser]:
    dbm('Getting all enabled instagram users')
    return InstagramUser.select().where(InstagramUser.enabled == True).order_by(InstagramUser.username).execute()


def get_telegram_user_active_instagram_account(user_id) -> InstagramAccount:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user active instagram account')
    return InstagramAccount.select().where(
        (InstagramAccount.added_by == telegram_user.id) & (InstagramAccount.is_active == True)).first()


def get_telegram_user_instagram_users_paginated(user_id, page) -> list[InstagramUser]:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram users')
    return InstagramUser.select().join(TelegramUserInstagramUsers).where(
        TelegramUserInstagramUsers.telegramuser_id == telegram_user).order_by(
        InstagramUser.username).paginate(
        page, 5).execute()


def check_telegram_user_in_instagram_user(instagram_user, telegram_user):
    instagram_user_available_for = TelegramUserInstagramUsers.select().join(TelegramUser).where(
        (TelegramUserInstagramUsers.instagramuser_id == instagram_user) & (
                TelegramUserInstagramUsers.telegramuser_id == telegram_user)).first()
    if instagram_user_available_for is None:
        return False
    else:
        return True


def get_telegram_user_instagram_users(user_id) -> list[InstagramUser]:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram users')
    return InstagramUser.select().join(TelegramUserInstagramUsers).where(
        (TelegramUserInstagramUsers.telegramuser_id == telegram_user) | (
                InstagramUser.added_by == telegram_user.id)).order_by(
        InstagramUser.username).execute()


def get_instagram_accounts_by_telegram_user_id(user_id) -> list[InstagramAccount]:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user instagram accounts')
    return InstagramAccount.select(InstagramAccount.username).where(
        (InstagramAccount.added_by == telegram_user.id) & (InstagramAccount.is_deleted == False)).execute()


def select_instagram_account(username, user_id):
    telegram_user = get_current_telegram_user(user_id)
    dbm('Selecting instagram account')
    telegram_user.selected_instagram_account = username
    telegram_user.save()
    return get_selected_instagram_account(user_id)


def get_selected_instagram_account(user_id) -> InstagramAccount:
    telegram_user = get_current_telegram_user(user_id)
    dbm('Getting telegram user selected instagram account')
    return InstagramAccount.select().where(
        (InstagramAccount.username == telegram_user.selected_instagram_account) & (
                InstagramAccount.added_by == telegram_user.id)).first()


def get_current_telegram_user(user_id) -> TelegramUser:
    dbm('Getting current telegram user')
    return TelegramUser.select().where(TelegramUser.user_id == user_id).first()


def get_instagram_user_by_username(username: str) -> InstagramUser:
    return InstagramUser.select().where(InstagramUser.username == username).first()


def get_iu_posts_by_page(instagram_user: InstagramUser, page: int) -> InstagramPost:
    return InstagramPostResource.select().join(InstagramPost).join(InstagramUser).where(
        InstagramUser.pk == instagram_user.pk).order_by(
        InstagramPost.taken_at).paginate(page, 1).first()


def get_iu_posts_count(instagram_user: InstagramUser) -> int:
    return InstagramPostResource.select().join(InstagramPost).join(InstagramUser).where(
        InstagramUser.pk == instagram_user.pk).order_by(
        InstagramPost.taken_at).count()


def get_iu_post_resources(instagram_post: InstagramPost) -> list[InstagramPostResource]:
    return InstagramPostResource.select().join(InstagramPost).where(
        (InstagramPost.pk == instagram_post.pk) & (InstagramPostResource.telegram_file_id != '')
    ).execute()


def get_iu_stories_by_page(instagram_user: InstagramUser, page: int) -> InstagramStory:
    return InstagramStory.select().join(InstagramUser).where(
        (InstagramStory.user == instagram_user) & (InstagramStory.telegram_file_id != '')).order_by(
        InstagramStory.taken_at).paginate(page, 1).first()


def get_iu_stories_count(instagram_user: InstagramUser) -> int:
    return InstagramStory.select().join(InstagramUser).where(
        (InstagramStory.user == instagram_user) & (InstagramStory.telegram_file_id != '')).order_by(
        InstagramStory.taken_at).count()


def get_iu_highlights_by_page(instagram_user: InstagramUser, page: int) -> InstagramHighlight:
    return InstagramHighlight.select().join(InstagramUser).where(
        (InstagramHighlight.user == instagram_user) & (InstagramHighlight.telegram_file_id != '')).order_by(
        InstagramHighlight.taken_at).paginate(page, 1).first()


def get_iu_highlights_count(instagram_user: InstagramUser) -> int:
    return InstagramHighlight.select().join(InstagramUser).where(
        (InstagramHighlight.user == instagram_user) & (InstagramHighlight.telegram_file_id != '')).order_by(
        InstagramHighlight.taken_at).count()
