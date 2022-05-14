from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from database.database import select_instagram_account, toggle_selected_active_instagram_account, \
    get_selected_instagram_account, set_selected_instagram_account_validity, add_instagram_account, \
    delete_selected_instagram_account
from bot.markups.markups import user_instagram_accounts_markup, user_selected_instagram_account_markup
from utils.misc import check_instagram_account_validity


def user_add_instagram_account(call: CallbackQuery, bot: TeleBot):
    msg = bot.edit_message_text('Write instagram username in next message', call.message.chat.id,
                                call.message.message_id)
    bot.register_next_step_handler(msg, instagram_process_add_user_instagram_account, call, bot)


def user_delete_instagram_account(call: CallbackQuery, bot: TeleBot):
    delete_selected_instagram_account(call.from_user.id)
    bot.edit_message_text('Instagram accounts', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_accounts_markup(call.from_user.id))


def user_instagram_accounts(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Instagram accounts', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_accounts_markup(call.from_user.id))


def user_select_instagram_account(call: CallbackQuery, bot: TeleBot):
    username = call.data.partition('user_select_instagram_account:')[2]
    selected = select_instagram_account(username, call.from_user.id)
    bot.edit_message_text(
        f'Selected {selected.username}\n'
        f'Instagram status: {"Valid" if selected.is_valid else "Invalid"}\n'
        f'Last instagram validation: {selected.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}',
        call.message.chat.id, call.message.message_id,
        reply_markup=user_selected_instagram_account_markup(selected))


def user_instagram_account_change_active(call: CallbackQuery, bot: TeleBot):
    selected = toggle_selected_active_instagram_account(call.from_user.id)
    bot.edit_message_text(
        f'Selected {selected.username}\n'
        f'Instagram status: {"Valid" if selected.is_valid else "Invalid"}\n'
        f'Last instagram validation: {selected.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}',
        call.message.chat.id, call.message.message_id,
        reply_markup=user_selected_instagram_account_markup(selected))


def user_instagram_account_check_status(call: CallbackQuery, bot: TeleBot):
    selected = get_selected_instagram_account(call.from_user.id)
    is_valid = check_instagram_account_validity(selected)
    updated = set_selected_instagram_account_validity(call.from_user.id, is_valid)
    bot.edit_message_text(
        f'Selected {updated.username}\n'
        f'Instagram status: {"Valid" if updated.is_valid else "Invalid"}\n'
        f'Last instagram validation: {updated.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}',
        call.message.chat.id, call.message.message_id,
        reply_markup=user_selected_instagram_account_markup(updated))


# Default next step handlers
def instagram_process_add_user_instagram_account(message: Message, call: CallbackQuery, bot: TeleBot):
    username = message.text
    msg = bot.edit_message_text('Write instagram password in next message', call.message.chat.id,
                                call.message.message_id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.register_next_step_handler(msg, instagram_process_add_user_instagram_account_password, call, username, bot)


def instagram_process_add_user_instagram_account_password(message: Message, call: CallbackQuery, username,
                                                          bot: TeleBot):
    password = message.text
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    add_instagram_account(username, password, call.from_user.id)
    bot.edit_message_text('Account added', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_accounts_markup(call.from_user.id))
