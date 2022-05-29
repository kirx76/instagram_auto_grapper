import threading
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import TeleBot
from telebot.custom_filters import SimpleCustomFilter
from telebot.types import Message, CallbackQuery

from bot.markups.markups import main_menu_markup, user_instagram_users_markup
from database.get import get_current_telegram_user, get_telegram_user_active_instagram_account, \
    get_enabled_instagram_users, get_telegram_user_by_instagram_user_username, \
    get_active_instagram_account_by_instagram_user
from database.set import create_db_telegram_user, save_instagram_account_dump_data
from instagram.instances.highlight import get_new_highlights, grap_highlights
from instagram.instances.post import get_new_posts, grap_posts
from instagram.instances.story import get_new_stories, grap_stories
from utils.misc import err, inst, initialize_valid_instagram_account, PseudoTelegramChat


def send_start(message: Message, bot: TeleBot):
    create_db_telegram_user(message.from_user.username, message.from_user.id)
    bot.send_message(message.chat.id, 'Welcome', reply_markup=main_menu_markup())


def user_main_menu(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_text('Main menu', call.message.chat.id, call.message.message_id,
                          reply_markup=main_menu_markup())


def characters_page_callback(call, bot):
    page = call.data.partition('user_instagram_user_page:')[2]
    bot.edit_message_text('Your instagram users', call.message.chat.id, call.message.message_id,
                          reply_markup=user_instagram_users_markup(call.message.chat.id, int(page)))


# MIDDLEWARES
DATA = {}


def antispam_func(bot: TeleBot, message: Message):
    bot.temp_data = {message.from_user.id: 'OK'}
    if DATA.get(message.from_user.id):
        if int(time.time()) - DATA[message.from_user.id] < 5:
            bot.temp_data = {message.from_user.id: 'FAIL'}
            bot.send_message(message.chat.id, 'You are making request too often')
            return
    DATA[message.from_user.id] = message.date


# FILTERS

def get_chat_id_from_initiator(initiator: CallbackQuery or Message):
    if hasattr(initiator, 'message'):
        return initiator.message.chat.id
    else:
        return initiator.chat.id


class AdminFilter(SimpleCustomFilter):
    key = 'admin'

    def check(self, initiator):
        telegram_user = get_current_telegram_user(get_chat_id_from_initiator(initiator))
        if telegram_user is None:
            return False

        if telegram_user.status.name == 'Admin':
            return True
        else:
            return False


class UsualFilter(SimpleCustomFilter):
    key = 'usual'

    def check(self, initiator):
        telegram_user = get_current_telegram_user(get_chat_id_from_initiator(initiator))
        if telegram_user is None:
            return False

        if telegram_user.status.name == 'Usual':
            return True
        else:
            return False


class NormalFilter(SimpleCustomFilter):
    key = 'normal'

    def check(self, initiator):
        telegram_user = get_current_telegram_user(get_chat_id_from_initiator(initiator))
        if telegram_user is None:
            return False

        if telegram_user.status.name == 'Normal':
            return True
        else:
            return False


class VIPFilter(SimpleCustomFilter):
    key = 'vip'

    def check(self, initiator):
        telegram_user = get_current_telegram_user(get_chat_id_from_initiator(initiator))
        if telegram_user is None:
            return False

        if telegram_user.status.name == 'VIP':
            return True
        else:
            return False


class BannedFilter(SimpleCustomFilter):
    key = 'banned'

    def check(self, initiator):
        telegram_user = get_current_telegram_user(get_chat_id_from_initiator(initiator))
        if telegram_user is None:
            return False

        if telegram_user.status.name == 'banned':
            return True
        else:
            return False


class DownloadingFilter(SimpleCustomFilter):
    def __init__(self, bot: TeleBot):
        self.bot = bot

    key = 'downloading'

    def answer_user_if_check_undone(self, initiator, active_instagram_account):
        if hasattr(initiator, 'message'):
            self.bot.edit_message_text(f'Your instagram account {active_instagram_account.username} '
                                       f'currently have a work, wait for it',
                                       initiator.message.chat.id, initiator.message.message_id)
        else:
            self.bot.send_message(initiator.chat.id,
                                  f'Your instagram account {active_instagram_account.username} '
                                  f'currently have a work, wait for it')

    def check(self, initiator: CallbackQuery or Message):
        active_instagram_account = get_telegram_user_active_instagram_account(
            get_chat_id_from_initiator(initiator))

        if active_instagram_account is None:
            return False

        if active_instagram_account.downloading_now:
            self.answer_user_if_check_undone(initiator, active_instagram_account)

        return active_instagram_account.downloading_now


# SCHEDULLER
def main_scheduler(bot):
    scheduler = BlockingScheduler()
    scheduler.add_job(main_scheduler_thread, 'interval', hours=1, args=(bot,))
    scheduler.start()


def main_scheduler_thread(bot: TeleBot):
    enabled_users = get_enabled_instagram_users()
    for user in enabled_users:
        inst(user.username)
        telegram_user = get_telegram_user_by_instagram_user_username(user.username)
        instagram_user_active_instagram_account = get_active_instagram_account_by_instagram_user(user)
        if instagram_user_active_instagram_account is None:
            err(f"Instagram user {user.username} don't have active Instagram account")
            return
        instagram_client = initialize_valid_instagram_account(instagram_user_active_instagram_account, bot,
                                                              telegram_user.user_id, save_instagram_account_dump_data)
        downloader(user, instagram_client, bot, telegram_user)


def downloader(instagram_user, instagram_client, bot, telegram_user):
    # TODO ADD MULTIPLE INSTAGRAM ACCOUNTS DOWNLOADING
    message = PseudoTelegramChat(telegram_user.user_id)

    try:
        new_stories = get_new_stories(instagram_user, instagram_client)
        if len(new_stories) > 0:
            bot.send_message(telegram_user.user_id,
                             f'User {instagram_user.username} have {len(new_stories)} new stories')
            default_downloader_thread_starter(grap_stories, bot, message, instagram_user, instagram_client,
                                              pks=new_stories)
        new_posts = get_new_posts(instagram_user, instagram_client)
        if len(new_posts) > 0:
            bot.send_message(telegram_user.user_id,
                             f'User {instagram_user.username} have {len(new_posts)} new posts')
            default_downloader_thread_starter(grap_posts, bot, message, instagram_user, instagram_client,
                                              pks=new_posts)

        new_highlights = get_new_highlights(instagram_user, instagram_client)
        if len(new_highlights) > 0:
            bot.send_message(telegram_user.user_id,
                             f'User {instagram_user.username} have {len(new_highlights)} new highlights')
            default_downloader_thread_starter(grap_highlights, bot, message, instagram_user,
                                              instagram_client, pks=new_highlights)
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)


def default_downloader_thread_starter(func, bot, message, instagram_user, valid_instagram_account, pks):
    try:
        default_downloader_thread = threading.Thread(target=func, args=(
            bot, message, instagram_user, valid_instagram_account, pks))
        default_downloader_thread.start()
        default_downloader_thread.join()
    except Exception as e:
        err(e)
