from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from bot.markups.markups import user_instagram_users_markup, iu_i_menu_markup, \
    iu_i_page_markup
from database.get import get_instagram_user_by_username, \
    get_iu_highlights_by_page, get_iu_stories_by_page, get_iu_posts_by_page
from database.set import add_instagram_user, toggle_iu_active
from instagram.main import get_media, resend_file
from utils.misc import get_username_from_url, caption_for_interactive_menu


def iu_i_action(call: CallbackQuery, bot: TeleBot):
    data = call.data.partition('iu_i_action:')[2]
    select = data.split('/')
    action = select[0]
    instagram_user_username = select[1]
    print(action, instagram_user_username)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if 'download_' in action:
        target_for_get = action.partition('download_')[2]
        instagram_user = get_instagram_user_by_username(instagram_user_username)
        msg = bot.send_photo(chat_id=call.message.chat.id, photo=instagram_user.profile_pic_location,
                             caption=f'Start collecting {target_for_get}')
        get_media(bot, msg, instagram_user, target_for_get)
    else:
        if action == 'activate_user':
            toggle_iu_active(instagram_user_username, True)
        elif action == 'deactivate_user':
            toggle_iu_active(instagram_user_username, False)
        updated_user = get_instagram_user_by_username(instagram_user_username)

        bot.send_photo(chat_id=call.message.chat.id, photo=updated_user.profile_pic_location,
                       reply_markup=iu_i_menu_markup(updated_user),
                       caption=caption_for_interactive_menu(updated_user))


def ius_list(call: CallbackQuery, bot: TeleBot):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Your instagram users',
                     reply_markup=user_instagram_users_markup(call.message.chat.id, 1))


def iu_i_menu(call: CallbackQuery, bot: TeleBot):
    instagram_user_username = call.data.partition('instagram_user_interactive_menu:')[2]
    instagram_user = get_instagram_user_by_username(instagram_user_username)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(chat_id=call.message.chat.id, photo=instagram_user.profile_pic_location,
                   reply_markup=iu_i_menu_markup(instagram_user), caption=caption_for_interactive_menu(instagram_user))


def iu_i_page(call: CallbackQuery, bot: TeleBot):
    data = call.data.partition('iu_i_page_markup:')[2]
    select = data.split('/')
    page = select[0]
    target = select[1]
    instagram_user_username = select[2]
    instagram_user = get_instagram_user_by_username(instagram_user_username)
    if target == 'highlights' and instagram_user.highlights.select().count() > 0:
        highlight = get_iu_highlights_by_page(instagram_user, int(page))
        resend_file(highlight.telegram_file_id, bot, call.message,
                    reply_markup=iu_i_page_markup(instagram_user, target, int(page)))
    elif target == 'stories' and instagram_user.stories.select().count() > 0:
        story = get_iu_stories_by_page(instagram_user, int(page))
        resend_file(story.telegram_file_id, bot, call.message,
                    reply_markup=iu_i_page_markup(instagram_user, target, int(page)))
    elif target == 'posts' and instagram_user.posts.select().count() > 0:
        post_resource = get_iu_posts_by_page(instagram_user, int(page))
        resend_file(post_resource.telegram_file_id, bot, call.message,
                    reply_markup=iu_i_page_markup(instagram_user, target, int(page)))


def user_instagram_users(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Your instagram users', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_users_markup(call.message.chat.id, 1))


def user_add_instagram_user(call: CallbackQuery, bot: TeleBot):
    msg = bot.edit_message_text('Write target username or paste profile url', call.message.chat.id,
                                call.message.message_id)
    bot.register_next_step_handler(msg, instagram_process_add_user_instagram_user, call, bot)


# Default next step handlers
def instagram_process_add_user_instagram_user(message: Message, call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Wait for check instagram user info', call.message.chat.id, call.message.message_id)
    target_username = get_username_from_url(message.text)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    add_instagram_user(target_username, call.message.chat.id, bot, call.message.chat.id)
    bot.edit_message_text('Your instagram users', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_users_markup(call.message.chat.id, 1))
