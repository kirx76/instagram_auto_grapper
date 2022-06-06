from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from bot.markups.user_markup import user_main_menu_markup, user_iaccounts_menu_markup, \
    user_selected_iaccount_menu_markup, user_iusers_menu_markup
from database.get import get_iaccount_by_username, get_tuser, get_tuser_iaccount
from database.set import create_or_get_tuser, create_or_get_iaccount
from instagram.main import check_iaccount_validity
from utils.bot_delete_message import bdm
from utils.bot_edit_message import bemt, bemp
from utils.get_instagram_username import get_instagram_username
from utils.models.IUserModel import IUserModel


def send_start(message: Message, bot: TeleBot):
    user = create_or_get_tuser(message)
    bot.send_message(message.chat.id, f'Welcome, {user.username}', reply_markup=user_main_menu_markup(user))


def user_main_menu(call: CallbackQuery, bot: TeleBot):
    user = get_tuser(call.from_user.id)
    bemt(bot, call.message, f'Welcome, {user.username}', reply_markup=user_main_menu_markup(user))


def user_iaccounts(call: CallbackQuery, bot: TeleBot):
    user = get_tuser(call.from_user.id)
    bemt(bot, call.message, 'Your instagram accounts list:', reply_markup=user_iaccounts_menu_markup(user))


def user_add_iaccount(call: CallbackQuery, bot: TeleBot):
    msg = bemt(bot, call.message, 'Write instagram account username below')
    bot.register_next_step_handler(msg, add_iaccount_process_username, call, bot)


def user_iaccount_menu(call: CallbackQuery, bot: TeleBot):
    iaccount_username = call.data.partition('user_iaccount_menu:')[2]
    iaccount = get_iaccount_by_username(iaccount_username)
    text = f'''Selected: <b>{iaccount.username}</b>
    
Owner: <b>{iaccount.owner.username}</b>
    '''
    print(iaccount)
    bemt(bot, call.message, text, reply_markup=user_selected_iaccount_menu_markup(iaccount))


def user_selected_iaccount_menu(call: CallbackQuery, bot: TeleBot):
    iaccount_username = call.data.partition('user_selected_iaccount_menu:')[2]
    iaccount = get_iaccount_by_username(iaccount_username)
    print(iaccount)


def user_iusers(call: CallbackQuery, bot: TeleBot):
    user = get_tuser(call.from_user.id)
    bemt(bot, call.message, 'Your instagram users list:', reply_markup=user_iusers_menu_markup(user))


def user_add_iuser(call: CallbackQuery, bot: TeleBot):
    msg = bemt(bot, call.message, 'Write instagram user username below')
    bot.register_next_step_handler(msg, add_iuser_process_username, call, bot)


def add_iuser_process_username(message: Message, call: CallbackQuery, bot: TeleBot):
    msg1 = bot.edit_message_text('Wait for check instagram user info', call.message.chat.id, call.message.message_id)
    iuser_username = get_instagram_username(message.text)
    tuser = get_tuser(call.from_user.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    iaccount = get_tuser_iaccount(tuser)
    iuser_model = IUserModel(iuser_username, iaccount)
    iuser_model.get_user_data()
    # iuser_model.save_to_db(owner=tuser)
    bdm(bot, msg1)
    msg = iuser_model.send_profile_pic_to_user(bot, call.message)

    iuser_model.save_to_db(owner=tuser)

    bemp(bot, msg, iuser_model.biggest_photo_id, 'User added')
    # is_iuser_valid, iuser_data = check_iuser_validity(tuser, iuser_username)
    # print('is_iuser_valid', is_iuser_valid)
    # create_or_get_iuser(iuser_data, tuser)
    # add_instagram_user(target_username, call.message.chat.id, bot, call.message.chat.id)
    # bot.edit_message_text('Your instagram users', call.message.chat.id, call.message.message_id,
    #                       reply_markup=user_instagram_users_markup(call.message.chat.id, 1))


# Default next step handlers
def add_iaccount_process_username(message: Message, call: CallbackQuery, bot: TeleBot):
    username = message.text
    msg = bot.edit_message_text('Write instagram password below', call.message.chat.id,
                                call.message.message_id)
    bot.delete_message(message.chat.id, message.message_id)
    bot.register_next_step_handler(msg, add_iaccount_process_password, call, username, bot)


def add_iaccount_process_password(message: Message, call: CallbackQuery, username: str, bot: TeleBot):
    bemt(bot, call.message, f'Wait for check account')
    password = message.text
    user = get_tuser(call.from_user.id)
    bot.delete_message(message.chat.id, message.message_id)
    is_iaccount_valid, message = check_iaccount_validity(username, password)
    if not is_iaccount_valid:
        bemt(bot, call.message, f'{message}', reply_markup=user_iaccounts_menu_markup(user))
    else:
        iaccount, created = create_or_get_iaccount(username, password, user)
        if created:
            bemt(bot, call.message, f'Account <b>{iaccount.username}</b> added',
                 reply_markup=user_iaccounts_menu_markup(user))
        else:
            bemt(bot, call.message, f'Account <b>{iaccount.username}</b> already exists',
                 reply_markup=user_iaccounts_menu_markup(user))
