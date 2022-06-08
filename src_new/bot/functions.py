from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from bot.markups.user_markup import user_main_menu_markup, user_iaccounts_menu_markup, \
    user_selected_iaccount_menu_markup, user_iusers_menu_markup, user_selected_iuser_menu_markup
from database.get import get_iaccount_by_username, get_tuser, get_tuser_iaccount, get_iuser_by_username
from database.set import create_or_get_tuser, create_or_get_iaccount
from instagram.main import check_iaccount_validity, get_media
from utils.bot_delete_message import bdm
from utils.bot_edit_message import bemt, bsm, bsp
from utils.get_instagram_username import get_instagram_username
from utils.models.IUserModel import IUserModel


def send_start(message: Message, bot: TeleBot):
    user = create_or_get_tuser(message)
    bsm(bot, message.chat.id, f'Welcome, {user.username}', reply_markup=user_main_menu_markup(user))


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


def user_selected_iuser_menu(call: CallbackQuery, bot: TeleBot):
    iuser_username = call.data.partition('user_selected_iuser_menu:')[2]
    iuser = get_iuser_by_username(iuser_username)
    user = get_tuser(call.from_user.id)
    bdm(bot, call.message)
    bsp(bot, user.user_id, iuser.telegram_file_id, f'Selected {iuser.username}', reply_markup=user_selected_iuser_menu_markup(iuser))


def user_action_selected_iuser(call: CallbackQuery, bot: TeleBot):
    data = call.data.partition('user_action_selected_iuser:')[2]
    selection = data.split('/')
    action = selection[0]
    iuser_username = selection[1]
    tuser = get_tuser(call.from_user.id)
    iuser = get_iuser_by_username(iuser_username)
    msg = bsp(bot, tuser.user_id, iuser.telegram_file_id, f'Start collecting {action}')
    iaccount = get_tuser_iaccount(tuser)
    iuser_model = IUserModel(iuser_username, iaccount)
    iuser_model.get_posts(bot, None)
    # get_media(bot, null, iuser_model, )
    print(action, iuser_username)


def add_iuser_process_username(message: Message, call: CallbackQuery, bot: TeleBot):
    msg1 = bot.edit_message_text('Wait for check instagram user info', call.message.chat.id, call.message.message_id)
    iuser_username = get_instagram_username(message.text)
    tuser = get_tuser(call.from_user.id)
    bdm(bot, message)
    iaccount = get_tuser_iaccount(tuser)
    iuser_model = IUserModel(iuser_username, iaccount)
    iuser_model.get_user_data()
    bdm(bot, msg1)
    msg = iuser_model.send_profile_pic_to_user(bot, call.message)
    iuser_model.save_to_db(owner=tuser)
    # bdm(bot, msg)
    bsm(bot, tuser.user_id, 'User added', reply_markup=user_iusers_menu_markup(tuser))


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
    bdm(bot, message)
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
