from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from database.database import get_instagram_accounts_by_telegram_user_id, get_telegram_user_instagram_subscriptions, \
    get_current_telegram_user

TEXTS = {
}


def main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Instagram accounts", callback_data='user_instagram_accounts'))
    markup.add(InlineKeyboardButton("Instagram subscriptions", callback_data='user_instagram_subscriptions'))
    # TODO WEB APPLICATION INITIALIZATION
    # markup.add(
    #     InlineKeyboardButton(text='hui', web_app=WebAppInfo(url="https://github.com/aiogram/aiogram/issues/891")))
    return markup


def user_instagram_accounts_markup(user_id):
    telegram_user = get_current_telegram_user(user_id)
    telegram_user_instagram_accounts = get_instagram_accounts_by_telegram_user_id(user_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Add instagram account', callback_data='user_add_instagram_account'))
    for account in telegram_user_instagram_accounts:
        markup.add(
            InlineKeyboardButton(account.username, callback_data=f'user_select_instagram_account:{account.username}'))
    if telegram_user.status.name == 'Admin':
        markup.add(InlineKeyboardButton("All instagram accounts", callback_data='admin_instagram_accounts'))
    markup.add(InlineKeyboardButton("Menu", callback_data='user_main_menu'))

    return markup


def user_selected_instagram_account_markup(instagram_account):
    markup = InlineKeyboardMarkup()
    if instagram_account.is_active:
        markup.add(InlineKeyboardButton("Turn off", callback_data='user_instagram_account:deactivate'))
    else:
        markup.add(InlineKeyboardButton("Turn on", callback_data='user_instagram_account:activate'))
    markup.add(InlineKeyboardButton('Delete account', callback_data='user_delete_instagram_account'))
    markup.add(InlineKeyboardButton('Check instagram status', callback_data='user_instagram_account_check_status'))
    markup.add(InlineKeyboardButton("Accounts menu", callback_data='user_instagram_accounts'))
    return markup


def user_instagram_subscriptions_markup(telegram_user):
    telegram_user_instagram_subscriptions = get_telegram_user_instagram_subscriptions(telegram_user)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Add instagram subscription', callback_data='user_add_instagram_subscription'))
    for subscription in telegram_user_instagram_subscriptions:
        markup.add(InlineKeyboardButton(subscription.username,
                                        callback_data=f'user_select_instagram_subscription:{subscription.username}'))
    markup.add(InlineKeyboardButton("Menu", callback_data='user_main_menu'))
    return markup


def user_selected_instagram_subscription_markup(instagram_subscription):
    markup = InlineKeyboardMarkup()
    posts_count = instagram_subscription.posts.select().count()
    stories_count = instagram_subscription.stories.select().count()
    highlights_count = instagram_subscription.highlights.select().count()
    if instagram_subscription.enabled:
        markup.add(InlineKeyboardButton("Turn off", callback_data='user_instagram_subscription:deactivate'))
    else:
        markup.add(InlineKeyboardButton("Turn on", callback_data='user_instagram_subscription:activate'))
    markup.add(
        InlineKeyboardButton(f"Posts: {posts_count}",
                             callback_data='user_instagram_subscription_get:posts'),
        InlineKeyboardButton(f"Stories: {stories_count}",
                             callback_data='user_instagram_subscription_get:stories'),
        InlineKeyboardButton(f"Highlights: {highlights_count}",
                             callback_data='user_instagram_subscription_get:highlights'))
    markup.add(InlineKeyboardButton("Subscriptions menu", callback_data='user_instagram_subscriptions'))
    return markup
