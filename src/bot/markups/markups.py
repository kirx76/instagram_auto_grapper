import math

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator

from database.get import get_current_telegram_user, get_instagram_accounts_by_telegram_user_id, \
    get_telegram_user_instagram_users, get_telegram_user_instagram_users_paginated, get_iu_highlights_count, \
    get_iu_stories_count

TEXTS = {
}


def main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Instagram accounts", callback_data='user_instagram_accounts'))
    markup.add(InlineKeyboardButton("Instagram users", callback_data='user_instagram_users'))
    # TODO WEB APPLICATION INITIALIZATION
    # markup.add(
    #     InlineKeyboardButton(text='hui', web_app=WebAppInfo(url="https://5caf-146-70-108-88.ngrok.io")))
    return markup


def iu_i_menu_markup(instagram_user):
    markup = InlineKeyboardMarkup()
    posts_count = instagram_user.posts.select().count()
    stories_count = instagram_user.stories.select().count()
    highlights_count = instagram_user.highlights.select().count()
    if instagram_user.enabled:
        markup.add(
            InlineKeyboardButton("Turn off", callback_data=f'iu_i_action:deactivate_user/{instagram_user.username}'))
    else:
        markup.add(
            InlineKeyboardButton("Turn on", callback_data=f'iu_i_action:activate_user/{instagram_user.username}'))
    markup.add(
        InlineKeyboardButton(f"Posts: {posts_count}",
                             callback_data=f'iu_i_action:download_posts/{instagram_user.username}'),
        InlineKeyboardButton(f"Stories: {stories_count}",
                             callback_data=f'iu_i_action:download_stories/{instagram_user.username}'),
        InlineKeyboardButton(f"Highlights: {highlights_count}",
                             callback_data=f'iu_i_action:download_highlights/{instagram_user.username}'))
    if posts_count > 0:
        markup.add(InlineKeyboardButton(f"Posts: {posts_count}",
                                        callback_data=f'iu_i_page_markup:1/posts/{instagram_user.username}'))
    if stories_count > 0:
        markup.add(InlineKeyboardButton(f"Stories: {stories_count}",
                                        callback_data=f'iu_i_page_markup:1/stories/{instagram_user.username}'))
    if highlights_count > 0:
        markup.add(InlineKeyboardButton(f"Highlights: {highlights_count}",
                                        callback_data=f'iu_i_page_markup:1/highlights/{instagram_user.username}'))
    markup.add(InlineKeyboardButton('Back to users list', callback_data=f'ius_list'))
    return markup


def iu_i_page_markup(instagram_user, target, page):
    if target == 'highlights':
        count = get_iu_highlights_count(instagram_user)
    elif target == 'stories':
        count = get_iu_stories_count(instagram_user)
    elif target == 'posts':
        count = 0
    else:
        print('PIZDOS')
        return
    paginator = InlineKeyboardPaginator(
        count,
        current_page=page,
        data_pattern='iu_i_page_markup:{page}' + f'/{target}/{instagram_user.username}'
    )
    paginator.add_after(
        InlineKeyboardButton("Back to user menu",
                             callback_data=f'instagram_user_interactive_menu:{instagram_user.username}'))
    return paginator.markup


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


def user_instagram_users_markup(telegram_user, page):
    telegram_user_instagram_users_all = get_telegram_user_instagram_users(telegram_user)
    telegram_user_instagram_users = get_telegram_user_instagram_users_paginated(telegram_user, page)
    paginator = InlineKeyboardPaginator(
        math.ceil(len(telegram_user_instagram_users_all) / 5),
        current_page=page,
        data_pattern='user_instagram_user_page:{page}'
    )
    for user in telegram_user_instagram_users:
        paginator.add_before(
            InlineKeyboardButton(user.username,
                                 callback_data=f'instagram_user_interactive_menu:{user.username}')
        )

    paginator.add_after(InlineKeyboardButton('Add instagram user', callback_data='user_add_instagram_user'),
                        InlineKeyboardButton("Menu", callback_data='user_main_menu'))
    return paginator.markup
