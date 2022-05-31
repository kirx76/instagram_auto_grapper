from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from bot.markups.markups import user_instagram_users_markup, user_selected_instagram_user_markup, \
    selected_instagram_user_interactive_markup
from database.get import select_instagram_user, get_selected_instagram_user, get_current_telegram_user, \
    get_selected_instagram_user_story_by_page
from database.set import toggle_selected_active_instagram_user, add_instagram_user
from instagram.main import get_media, get_sent_files, send_file
from utils.misc import get_username_from_url


def instagram_user_interactive_menu_data(call: CallbackQuery, bot: TeleBot):
    telegram_user = get_current_telegram_user(call.message.chat.id)
    selected_data = call.data.partition('instagram_user_interactive_menu:')[2]
    print(selected_data)
    if selected_data == 'stories':
        story = get_selected_instagram_user_story_by_page(telegram_user, 1)
        send_file(story.telegram_file_id, bot, call.message)
    elif selected_data == 'posts':
        pass
    elif selected_data == 'highlights':
        pass
    # post = get_selected_instagram_user_post_by_page(telegram_user, 1)
    # if post.telegram_file_id is None:
    #     print('POST WITH RESOURCES')
    #     resources = get_instagram_post_resources_by_post(post)
    #     for resource in resources:
    #         print(resource.pk)
    # else:
    #     print('SIMPLE POST')
    #     print(post.pk)
    # print(s)


def instagram_user_interactive_menu(call: CallbackQuery, bot: TeleBot):
    selected = get_selected_instagram_user(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(chat_id=call.message.chat.id, photo=selected.profile_pic_location,
                   reply_markup=selected_instagram_user_interactive_markup(selected))


def user_instagram_users(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Your instagram users', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_users_markup(call.message.chat.id, 1))


def user_add_instagram_user(call: CallbackQuery, bot: TeleBot):
    msg = bot.edit_message_text('Write target username or paste profile url', call.message.chat.id,
                                call.message.message_id)
    bot.register_next_step_handler(msg, instagram_process_add_user_instagram_user, call, bot)


def user_select_instagram_user(call: CallbackQuery, bot: TeleBot):
    selected_instagram_user = call.data.partition('user_select_instagram_user:')[2]
    instagram_user = select_instagram_user(selected_instagram_user, call.message.chat.id)
    bot.edit_message_text(f'Selected: {instagram_user.username}', call.message.chat.id,
                          call.message.message_id,
                          reply_markup=user_selected_instagram_user_markup(instagram_user))


def user_instagram_user_change_active(call: CallbackQuery, bot: TeleBot):
    instagram_user = toggle_selected_active_instagram_user(call.from_user.id)
    bot.edit_message_text(f'Selected: {instagram_user.username}',
                          call.message.chat.id, call.message.message_id,
                          reply_markup=user_selected_instagram_user_markup(instagram_user))


def user_instagram_user_get(call: CallbackQuery, bot: TeleBot):
    target_for_get = call.data.partition('user_instagram_user_get:')[2]
    target_instagram_user = get_selected_instagram_user(call.message.chat.id)
    bot.edit_message_text(f'Start collecting', call.message.chat.id, call.message.message_id)
    get_media(bot, call.message, target_instagram_user, target_for_get)


def user_instagram_user_get_sent(call: CallbackQuery, bot: TeleBot):
    target_for_get = call.data.partition('user_instagram_user_get_sent:')[2]
    target_instagram_user = get_selected_instagram_user(call.message.chat.id)
    bot.edit_message_text(f'Start collecting', call.message.chat.id, call.message.message_id)
    get_sent_files(bot, call.message, target_instagram_user, target_for_get)


# Default next step handlers
def instagram_process_add_user_instagram_user(message: Message, call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Wait for check instagram user info', call.message.chat.id, call.message.message_id)
    target_username = get_username_from_url(message.text)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    add_instagram_user(target_username, call.message.chat.id, bot, call.message.chat.id)
    bot.edit_message_text('Your instagram users', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_users_markup(call.message.chat.id, 1))
