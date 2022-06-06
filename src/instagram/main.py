import mimetypes
import os
import time

from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import InputMediaPhoto, InputMediaVideo

from bot.main import default_downloader_thread_starter
from bot.markups.markups import iu_i_menu_markup
from database.get import get_telegram_user_active_instagram_account
from database.set import save_iaccount_dump_data
from instagram.instances.highlight import get_new_highlights, grap_highlights
from instagram.instances.post import get_new_posts, grap_posts
from instagram.instances.story import get_new_stories, grap_stories
from utils.misc import initialize_valid_instagram_account, err, inst

load_dotenv()

TG_BOT_API_URL = os.environ.get("TG_BOT_API_URL")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")


def resend_file(file_id, bot: TeleBot, message, reply_markup=None):
    time.sleep(1)
    file_url = bot.get_file_url(file_id)
    if 'videos' in file_url:
        bot.edit_message_media(media=InputMediaVideo(file_id), chat_id=message.chat.id,
                               message_id=message.message_id, reply_markup=reply_markup)
    elif 'photos' in file_url:
        bot.edit_message_media(media=InputMediaPhoto(file_id), chat_id=message.chat.id,
                               message_id=message.message_id, reply_markup=reply_markup)
    else:
        mt = mimetypes.guess_type(file_url)
        if mt[0] == 'video/mp4':
            bot.edit_message_media(media=InputMediaVideo(file_id), chat_id=message.chat.id,
                                   message_id=message.message_id, reply_markup=reply_markup)
        else:
            bot.edit_message_media(media=InputMediaPhoto(file_id), chat_id=message.chat.id,
                                   message_id=message.message_id, reply_markup=reply_markup)


def get_media(bot: TeleBot, message, instagram_user, target):
    try:
        inst(f'Current target: {instagram_user.username}')
        active_instagram_account = get_telegram_user_active_instagram_account(message.chat.id)
        valid_instagram_account = initialize_valid_instagram_account(active_instagram_account, bot, message.chat.id,
                                                                     save_iaccount_dump_data)

        if target == 'posts':
            new_posts = get_new_posts(instagram_user, valid_instagram_account)
            if len(new_posts) > 0:
                default_downloader_thread_starter(grap_posts, bot, message, instagram_user, valid_instagram_account,
                                                  pks=new_posts)
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_photo(chat_id=message.chat.id, photo=instagram_user.profile_pic_location,
                               reply_markup=iu_i_menu_markup(instagram_user),
                               caption='No new posts')

        if target == 'stories':
            new_stories = get_new_stories(instagram_user, valid_instagram_account)
            if len(new_stories) > 0:
                default_downloader_thread_starter(grap_stories, bot, message, instagram_user, valid_instagram_account,
                                                  pks=new_stories)
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_photo(chat_id=message.chat.id, photo=instagram_user.profile_pic_location,
                               reply_markup=iu_i_menu_markup(instagram_user),
                               caption='No new stories')

        if target == 'highlights':
            new_highlights = get_new_highlights(instagram_user, valid_instagram_account)
            if len(new_highlights) > 0:
                default_downloader_thread_starter(grap_highlights, bot, message, instagram_user,
                                                  valid_instagram_account,
                                                  pks=new_highlights)
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_photo(chat_id=message.chat.id, photo=instagram_user.profile_pic_location,
                               reply_markup=iu_i_menu_markup(instagram_user),
                               caption='No new highlights')
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
