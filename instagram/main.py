import mimetypes
import os
import time

from dotenv import load_dotenv
from telebot import TeleBot

from bot.main import default_downloader_thread_starter
from bot.markups.markups import user_selected_instagram_user_markup
from database.get import get_telegram_user_active_instagram_account, get_instagram_posts_with_file_id_by_instagram_user, \
    get_instagram_stories_with_file_id_by_instagram_user, get_instagram_highlights_with_file_id_by_instagram_user
from instagram.instances.highlight import get_new_highlights, grap_highlights
from instagram.instances.post import get_new_posts, grap_posts
from instagram.instances.story import get_new_stories, grap_stories
from utils.misc import initialize_valid_instagram_account, err, inst

load_dotenv()

TG_BOT_API_URL = os.environ.get("TG_BOT_API_URL")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")


def get_sent_files(bot: TeleBot, message, instagram_user, target):
    try:
        inst(f'Current target for sent files: {instagram_user.username}')

        if target == 'posts':
            posts = get_instagram_posts_with_file_id_by_instagram_user(instagram_user)
            for post in posts:
                try:
                    time.sleep(1)
                    file_url = bot.get_file_url(post.telegram_file_id)
                    print(file_url)
                    mt = mimetypes.guess_type(file_url)
                    print(mt, mt[0])
                    if mt[0] == 'video/mp4':
                        bot.send_video(message.chat.id, video=post.telegram_file_id)
                    else:
                        bot.send_photo(message.chat.id, photo=post.telegram_file_id)
                except Exception as e:
                    err(f'{post}{e}')
                    pass

        if target == 'stories':
            stories = get_instagram_stories_with_file_id_by_instagram_user(instagram_user)
            for story in stories:
                try:
                    time.sleep(1)
                    file_url = bot.get_file_url(story.telegram_file_id)
                    print(file_url)
                    mt = mimetypes.guess_type(file_url)
                    print(mt, mt[0])
                    if mt[0] == 'video/mp4':
                        bot.send_video(message.chat.id, video=story.telegram_file_id)
                    else:
                        bot.send_photo(message.chat.id, photo=story.telegram_file_id)
                except Exception as e:
                    err(f'{story}{e}')
                    pass

        if target == 'highlights':
            highlights = get_instagram_highlights_with_file_id_by_instagram_user(instagram_user)
            for highlight in highlights:
                try:
                    time.sleep(1)
                    file_url = bot.get_file_url(highlight.telegram_file_id)
                    print(file_url)
                    mt = mimetypes.guess_type(file_url)
                    print(mt, mt[0])
                    if mt[0] == 'video/mp4':
                        bot.send_video(message.chat.id, video=highlight.telegram_file_id)
                    else:
                        bot.send_photo(message.chat.id, photo=highlight.telegram_file_id)
                except Exception as e:
                    err(f'{highlight}{e}')
                    pass

    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)


def get_media(bot: TeleBot, message, instagram_user, target):
    try:
        inst(f'Current target: {instagram_user.username}')
        active_instagram_account = get_telegram_user_active_instagram_account(message.chat.id)
        valid_instagram_account = initialize_valid_instagram_account(active_instagram_account, bot, message.chat.id)

        if target == 'posts':
            new_posts = get_new_posts(instagram_user, valid_instagram_account)
            if len(new_posts) > 0:
                default_downloader_thread_starter(grap_posts, bot, message, instagram_user, valid_instagram_account,
                                                  pks=new_posts)
            else:
                bot.edit_message_text('No new posts', message.chat.id, message.message_id,
                                      reply_markup=user_selected_instagram_user_markup(instagram_user))

        if target == 'stories':
            new_stories = get_new_stories(instagram_user, valid_instagram_account)
            if len(new_stories) > 0:
                default_downloader_thread_starter(grap_stories, bot, message, instagram_user, valid_instagram_account,
                                                  pks=new_stories)
            else:
                bot.edit_message_text('No new stories', message.chat.id, message.message_id,
                                      reply_markup=user_selected_instagram_user_markup(instagram_user))

        if target == 'highlights':
            new_highlights = get_new_highlights(instagram_user, valid_instagram_account)
            if len(new_highlights) > 0:
                default_downloader_thread_starter(grap_highlights, bot, message, instagram_user,
                                                  valid_instagram_account,
                                                  pks=new_highlights)
            else:
                bot.edit_message_text('No new highlights', message.chat.id, message.message_id,
                                      reply_markup=user_selected_instagram_user_markup(instagram_user))
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
