from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from database.database import select_instagram_subscription, toggle_selected_active_instagram_subscription, \
    get_selected_instagram_subscription, add_instagram_subscription
from instagram.main import get_media
from bot.markups.markups import user_instagram_subscriptions_markup, user_selected_instagram_subscription_markup
from utils.misc import get_username_from_url


def user_instagram_subscriptions(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Your subscriptions', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_subscriptions_markup(call.message.chat.id))


def user_add_instagram_subscription(call: CallbackQuery, bot: TeleBot):
    msg = bot.edit_message_text('Write target username or paste profile url', call.message.chat.id,
                                call.message.message_id)
    bot.register_next_step_handler(msg, instagram_process_add_user_instagram_subscription, call, bot)


def user_select_instagram_subscription(call: CallbackQuery, bot: TeleBot):
    selected_instagram_subscription = call.data.partition('user_select_instagram_subscription:')[2]
    instagram_subscription = select_instagram_subscription(selected_instagram_subscription, call.message.chat.id)
    bot.edit_message_text(f'Selected: {instagram_subscription.username}', call.message.chat.id,
                          call.message.message_id,
                          reply_markup=user_selected_instagram_subscription_markup(instagram_subscription))


def user_instagram_subscription_change_active(call: CallbackQuery, bot: TeleBot):
    instagram_subscription = toggle_selected_active_instagram_subscription(call.from_user.id)
    bot.edit_message_text(f'Selected: {instagram_subscription.username}',
                          call.message.chat.id, call.message.message_id,
                          reply_markup=user_selected_instagram_subscription_markup(instagram_subscription))


def user_instagram_subscription_get(call: CallbackQuery, bot: TeleBot):
    target_for_get = call.data.partition('user_instagram_subscription_get:')[2]
    target_instagram_subscription = get_selected_instagram_subscription(call.message.chat.id)
    msg = bot.edit_message_text(f'Start collecting', call.message.chat.id, call.message.message_id)
    get_media(bot, call.message, target_instagram_subscription, target_for_get)
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    bot.send_message(call.message.chat.id,
                     f'Collection complete\n\nSelected: {target_instagram_subscription.username}',
                     reply_markup=user_selected_instagram_subscription_markup(target_instagram_subscription))


# Default next step handlers
def instagram_process_add_user_instagram_subscription(message: Message, call: CallbackQuery, bot: TeleBot):
    target_username = get_username_from_url(message.text)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    add_instagram_subscription(target_username, call.message.chat.id)
    bot.edit_message_text('Your subscriptions', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_subscriptions_markup(call.message.chat.id))
