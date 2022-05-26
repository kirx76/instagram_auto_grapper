from telebot import TeleBot
from telebot.types import CallbackQuery

from src.bot.markups.admin_markups import admin_instagram_accounts_markup, admin_selected_instagram_account_markup
from src.database.get import select_instagram_account
from src.database.set import restore_selected_instagram_account


def admin_instagram_accounts(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('All instagram accounts', call.message.chat.id, call.message.message_id,
                          reply_markup=admin_instagram_accounts_markup())


def admin_restore_instagram_account(call: CallbackQuery, bot: TeleBot):
    selected = restore_selected_instagram_account(call.from_user.id)
    bot.edit_message_text(
        f'Selected {selected.username}\n'
        f'Instagram status: {"Valid" if selected.is_valid else "Invalid"}\n'
        f'Deleted: {"Yes" if selected.is_deleted else "No"}\n'
        f'Active: {"Yes" if selected.is_active else "No"}\n'
        f'Downloading now: {"Yes" if selected.downloading_now else "No"}\n'
        f'Last instagram validation: {selected.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'Created at: {selected.created_at.strftime("%Y-%m-%d %H:%M:%S")}',
        call.message.chat.id, call.message.message_id,
        reply_markup=admin_selected_instagram_account_markup(selected))


def admin_select_instagram_account(call: CallbackQuery, bot: TeleBot):
    username = call.data.partition('admin_select_instagram_account:')[2]
    selected = select_instagram_account(username, call.from_user.id)
    bot.edit_message_text(
        f'Selected {selected.username}\n'
        f'Instagram status: {"Valid" if selected.is_valid else "Invalid"}\n'
        f'Deleted: {"Yes" if selected.is_deleted else "No"}\n'
        f'Active: {"Yes" if selected.is_active else "No"}\n'
        f'Downloading now: {"Yes" if selected.downloading_now else "No"}\n'
        f'Last instagram validation: {selected.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'Created at: {selected.created_at.strftime("%Y-%m-%d %H:%M:%S")}',
        call.message.chat.id, call.message.message_id,
        reply_markup=admin_selected_instagram_account_markup(selected))
