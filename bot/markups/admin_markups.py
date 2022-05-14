from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.database import get_all_instagram_accounts_for_admin


def admin_instagram_accounts_markup():
    instagram_accounts = get_all_instagram_accounts_for_admin()
    markup = InlineKeyboardMarkup()
    for instagram_account in instagram_accounts:
        markup.add(InlineKeyboardButton(
            f'{instagram_account.username} - {"Deleted" if instagram_account.is_deleted else "Active"}',
            callback_data=f'admin_select_instagram_account:{instagram_account.username}'))
    return markup


def admin_selected_instagram_account_markup(instagram_account):
    markup = InlineKeyboardMarkup()
    if instagram_account.is_active:
        markup.add(InlineKeyboardButton("Turn off", callback_data='user_instagram_account:deactivate'))
    else:
        markup.add(InlineKeyboardButton("Turn on", callback_data='user_instagram_account:activate'))
    if instagram_account.is_deleted:
        markup.add(InlineKeyboardButton('Restore account', callback_data='admin_restore_instagram_account'))
    else:
        markup.add(InlineKeyboardButton('Delete account', callback_data='user_delete_instagram_account'))
    markup.add(InlineKeyboardButton("Accounts menu", callback_data='user_instagram_accounts'))
    return markup
