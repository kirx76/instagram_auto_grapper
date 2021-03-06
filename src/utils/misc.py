import os
import re
import shutil
import time
from logging import Formatter, FileHandler, getLogger, DEBUG
from urllib.parse import urlparse

import boto3
import telebot
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientLoginRequired, LoginRequired, TwoFactorRequired, PleaseWaitFewMinutes, \
    ChallengeRequired

logger = getLogger('__main__')
logger.setLevel(DEBUG)

handler = FileHandler('logs.txt')
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)

load_dotenv()

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
IG_DUMP_FOLDER_PATH = os.environ.get("IG_DUMP_FOLDER_PATH")
BOTO3_ACCESS_KEY = os.environ.get("BOTO3_ACCESS_KEY")
BOTO3_SECRET_KEY = os.environ.get("BOTO3_SECRET_KEY")
BOTO3_SESSION_TOKEN = os.environ.get("BOTO3_SESSION_TOKEN")
BOTO3_BUCKET_NAME = os.environ.get("BOTO3_BUCKET_NAME")
BOTO3_ENDPOINT_URL = os.environ.get("BOTO3_ENDPOINT_URL")
PROXY = os.environ.get("PROXY")


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CVIOLET = '\33[35m'
    CBLUE = '\33[34m'
    CBEIGE = '\33[36m'


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        logger.exception('exception')
        return False


def get_username_from_url(url):
    if is_url(url):
        return re.search('(?:(?:http|https):\/\/)?(?:www\.)?(?:instagram\.com|instagr\.am)\/([A-Za-z0-9-_\.]+)', url)[1]
    else:
        return url


def tg(message):
    logger.debug(f'[TELEGRAM]: {message}')
    print(f'{BColors.BOLD}{BColors.CBLUE}[TELEGRAM]{BColors.ENDC} {message}')


def oss(message):
    logger.debug(f'[SYSTEM]: {message}')
    print(f'{BColors.BOLD}{BColors.CBEIGE}[SYSTEM]{BColors.ENDC} {message}')


def inst(message):
    logger.debug(f'[INSTAGRAM]: {message}')
    print(f'{BColors.BOLD}{BColors.CVIOLET}[INSTAGRAM]{BColors.ENDC} {message}')


def dbm(message):
    logger.debug(f'[DATABASE]: {message}')
    print(f'{BColors.BOLD}{BColors.OKGREEN}[DATABASE]{BColors.ENDC} {message}')


def info(message):
    logger.debug(f'[INFO]: {message}')
    print(f'{BColors.BOLD}{BColors.WARNING}[INFO]{BColors.ENDC} {message}')


def menu(message):
    logger.debug(f'[MENU]: {message}')
    print(f'{BColors.BOLD}{BColors.OKCYAN}[MENU]{BColors.ENDC} {message}')


def err(message):
    logger.exception('exception')
    print(f'{BColors.FAIL}[ERROR] {message}{BColors.ENDC}')


def divider():
    print(f'{BColors.OKCYAN}{"=" * 50}{BColors.ENDC}')


def cleanup_downloaded_file_by_filepath(path):
    oss('Remove file by filepath')
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        err(e)


def cleanup_folder_by_username(username):
    oss('Remove folder with content')
    try:
        shutil.rmtree(f'./downloads/{username}')
    except OSError as e:
        err(f'{e.filename} - {e.strerror}')


def create_folder_by_username(username):
    oss('Start folder cleanup')
    cleanup_folder_by_username(username)
    oss('Creating new folder')
    os.mkdir(f'./downloads/{username}')
    oss('Creating complete')
    return f'./downloads/{username}'


class AWS:
    def __init__(self):
        self.session = boto3.session.Session(
            aws_access_key_id=BOTO3_ACCESS_KEY,
            aws_secret_access_key=BOTO3_SECRET_KEY,
        )
        self.client = self.session.client(
            service_name='s3',
            endpoint_url=BOTO3_ENDPOINT_URL
        )

    def upload_file(self, file_path: str, file_name: str):
        self.client.upload_file(file_path, BOTO3_BUCKET_NAME, file_name)
        return f'{BOTO3_ENDPOINT_URL}/{BOTO3_BUCKET_NAME}/{file_name}'


def initialize_telegram_bot(threads=5):
    tg('Start initialize telegram bot')
    tgbot = telebot.TeleBot(TG_BOT_TOKEN, parse_mode='HTML', num_threads=threads)
    tg('Telegram bot initialized')
    return tgbot


def caption_text_to_db(media):
    text = ''
    if hasattr(media, 'caption_text'):
        text = media.caption_text
    return text


def caption_for_interactive_menu(instagram_user):
    text = f'''
username: <b>{instagram_user.username}</b>
fullname: <b>{instagram_user.full_name}</b>
enabled: <b>{"Yes" if instagram_user.enabled else "No"}</b>
is_private: <b>{"Yes" if instagram_user.is_private else "No"}</b>
added_by: <b>{instagram_user.added_by.username}</b>
added_at: <b>{instagram_user.added_at.strftime("%Y-%m-%d %H:%M:%S")}</b>
'''
    return text


def collect_caption_to_send(media, username):
    text = f'username: #{username}'
    if hasattr(media, 'taken_at'):
        if media.taken_at is not None and media.taken_at != '':
            text = f'{text}\n\ndate: {media.taken_at.strftime("%Y-%m-%d %H:%M:%S")}'
    if hasattr(media, 'caption_text'):
        if media.caption_text is not None and media.caption_text != '':
            if len(media.caption_text) < 400:
                text = f'{text}\n\ncaption: {media.caption_text}'
    return text


def initialize_valid_instagram_account(instagram_account, bot, telegram_user_id, saver):
    # TODO ADD PROXIES
    is_valid = check_instagram_account_validity(instagram_account, bot, telegram_user_id, saver)
    if is_valid:
        cl = Client()
        dump_data = instagram_account.dump_data
        with open(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json', 'w') as f:
            f.write(dump_data)
        cl.load_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
        cl.login(instagram_account.username, instagram_account.password)
        cl.dump_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
        saver(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json', instagram_account)
    else:
        err('BAD INITIALIZE VALID INSTAGRAM ACCOUNT')
        raise SystemExit('BAD INITIALIZE VALID INSTAGRAM ACCOUNT')
    return cl


def process_challenge_two_factor_code(message, bot, telegram_user_id, instagram_account, saver):
    two_factor_code = message.text
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    check_instagram_account_validity(instagram_account, bot, telegram_user_id, saver, two_factor_code)


def check_instagram_account_validity(instagram_account, bot: telebot.TeleBot, telegram_user_id, saver,
                                     two_factor_code=None, relogin=False):
    code = ''
    attempts = 0
    inst(f'Start checking instagram account {instagram_account.username}')
    code = instagram_account.verification_code

    def process_challenge_code_handler(message, username):
        nonlocal code
        code = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    def challenge_code_handler(username, choice):
        nonlocal code, attempts
        if attempts > 3:
            err('ATTEMPTS TO VERIFY LARGER THAN 3')
            raise SystemExit('ATTEMPTS TO VERIFY LARGER THAN 3')
        if code is None:
            while True:
                attempts += 1
                msg = bot.send_message(telegram_user_id,
                                       'You have 1 minute to write your verification code in next message')
                bot.register_next_step_handler(msg, process_challenge_code_handler, username)
                bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                bot.send_message(telegram_user_id, 'Wait for check')
                time.sleep(60)
                if code and code.isdigit():
                    break
            return code
        else:
            return code

    try:
        cl = Client()
        cl.challenge_code_handler = challenge_code_handler
        # if PROXY is not None:
        #     cl.set_proxy(PROXY)

        dump_data = instagram_account.dump_data
        if dump_data is None:
            oss(f'No dump for user {instagram_account.username}')
            if two_factor_code is None:
                cl.login(instagram_account.username, instagram_account.password, True)
            else:
                cl.login(instagram_account.username, instagram_account.password, True,
                         verification_code=two_factor_code)
        else:
            oss(f'User {instagram_account.username} dump founded')
            with open(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json', 'w') as f:
                f.write(dump_data)
            cl.load_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
            if two_factor_code is None:
                cl.login(instagram_account.username, instagram_account.password, relogin=relogin)
            else:
                cl.login(instagram_account.username, instagram_account.password, verification_code=two_factor_code,
                         relogin=relogin)
        try:
            cl.get_timeline_feed()
            inst('Saving authorization dump')
            cl.dump_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
            saver(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json', instagram_account)
            inst('Login done')
            return True
        except ClientLoginRequired as e:
            err(e)
            if os.path.exists(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json'):
                os.remove(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
                return check_instagram_account_validity(instagram_account, bot, telegram_user_id, saver, relogin=True)
            return False
        except LoginRequired as e:
            err(e)
            if os.path.exists(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json'):
                os.remove(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
                return check_instagram_account_validity(instagram_account, bot, telegram_user_id, saver, relogin=True)
            return False
        except Exception as e:
            err(e)
            return False
    except TwoFactorRequired as e:
        err(e)
        msg = bot.send_message(telegram_user_id,
                               'Bad initialization, you need to write two-factor code in next message.')
        bot.register_next_step_handler(msg, process_challenge_two_factor_code, bot, telegram_user_id,
                                       instagram_account, saver)
    except PleaseWaitFewMinutes as e:
        err(e)
        time.sleep(60)
    except ChallengeRequired as e:
        err(e)
        s = cl.challenge_resolve(cl.last_json)
        print('SSSSSSS', s)
        d = cl.get_timeline_feed()
        print(d)
    except Exception as e:
        err(e)
    return False


class PseudoTelegramMessage:
    def __init__(self, user_id):
        self.id = user_id


class PseudoTelegramChat:
    def __init__(self, user_id):
        self.chat = PseudoTelegramMessage(user_id)
