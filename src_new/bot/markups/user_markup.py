from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.get import get_iaccounts_list, get_iusers_list
from database.models import TUser, IAccount, IUser


def user_main_menu_markup(tuser: TUser):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Instagram accounts", callback_data='user_iaccounts'))
    iaccounts_count = tuser.i_accounts.count()
    if iaccounts_count > 0:
        markup.add(InlineKeyboardButton("Instagram users", callback_data='user_iusers'))
    return markup


def user_iaccounts_menu_markup(tuser: TUser):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Add instagram account', callback_data='user_add_iaccount'))

    iaccounts = get_iaccounts_list(tuser)
    for iaccount in iaccounts:
        markup.add(InlineKeyboardButton(iaccount.username, callback_data=f'user_iaccount_menu:{iaccount.username}'))
    markup.add(InlineKeyboardButton('Back', callback_data=f'user_main_menu'))
    return markup


def user_selected_iaccount_menu_markup(iaccount: IAccount):
    markup = InlineKeyboardMarkup()
    # markup.add(InlineKeyboardButton('Check instagram status', callback_data=f'user_selected_iaccount_menu:{iaccount.username} => check'))
    markup.add(InlineKeyboardButton('Back', callback_data=f'user_iaccounts'))
    return markup


def user_iusers_menu_markup(tuser: TUser):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Add instagram user', callback_data='user_add_iuser'))

    iusers = get_iusers_list(tuser)
    for iuser in iusers:
        markup.add(InlineKeyboardButton(iuser.username, callback_data=f'user_selected_iuser_menu:{iuser.username}'))

    return markup


def user_selected_iuser_menu_markup(iuser: IUser):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Posts', callback_data=f'user_action_selected_iuser:posts/{iuser.username}'))
    markup.add(InlineKeyboardButton('Stories', callback_data=f'user_action_selected_iuser:stories/{iuser.username}'))
    markup.add(InlineKeyboardButton('Highlights', callback_data=f'user_action_selected_iuser:highlights/{iuser.username}'))

    markup.add(InlineKeyboardButton('Back', callback_data=f'user_iusers'))
    return markup
