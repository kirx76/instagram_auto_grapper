import os
import re
import shutil
from urllib.parse import urlparse

import boto3
import telebot
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientLoginRequired, LoginRequired

load_dotenv()

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
IG_DUMP_FOLDER_PATH = os.environ.get("IG_DUMP_FOLDER_PATH")
BOTO3_ACCESS_KEY = os.environ.get("BOTO3_ACCESS_KEY")
BOTO3_SECRET_KEY = os.environ.get("BOTO3_SECRET_KEY")
BOTO3_SESSION_TOKEN = os.environ.get("BOTO3_SESSION_TOKEN")
BOTO3_BUCKET_NAME = os.environ.get("BOTO3_BUCKET_NAME")
BOTO3_ENDPOINT_URL = os.environ.get("BOTO3_ENDPOINT_URL")


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
        return False


def get_username_from_url(url):
    if is_url(url):
        return re.search('(?:(?:http|https):\/\/)?(?:www\.)?(?:instagram\.com|instagr\.am)\/([A-Za-z0-9-_\.]+)', url)[1]
    else:
        return url


def tg(message):
    print(f'{BColors.BOLD}{BColors.CBLUE}[TELEGRAM]{BColors.ENDC} {message}')


def oss(message):
    print(f'{BColors.BOLD}{BColors.CBEIGE}[SYSTEM]{BColors.ENDC} {message}')


def inst(message):
    print(f'{BColors.BOLD}{BColors.CVIOLET}[INSTAGRAM]{BColors.ENDC} {message}')


def dbm(message):
    print(f'{BColors.BOLD}{BColors.OKGREEN}[DATABASE]{BColors.ENDC} {message}')


def info(message):
    print(f'{BColors.BOLD}{BColors.WARNING}[INFO]{BColors.ENDC} {message}')


def menu(message):
    print(f'{BColors.BOLD}{BColors.OKCYAN}[MENU]{BColors.ENDC} {message}')


def err(message):
    print(f'{BColors.FAIL}[ERROR] {message}{BColors.ENDC}')


def divider():
    print(f'{BColors.OKCYAN}{"=" * 50}{BColors.ENDC}')


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


def initialize_telegram_bot(threads=1):
    tg('Start initialize telegram bot')
    tgbot = telebot.TeleBot(TG_BOT_TOKEN, parse_mode='HTML', num_threads=threads)
    tg('Telegram bot initialized')
    return tgbot


def caption_text_to_db(media):
    text = ''
    if hasattr(media, 'caption_text'):
        text = media.caption_text
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


def initialize_valid_instagram_account(instagram_account):
    is_valid = check_instagram_account_validity(instagram_account)
    if is_valid:
        cl = Client()
        cl.load_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
        cl.login(instagram_account.username, instagram_account.password)
        cl.dump_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
    else:
        err('BAD INITIALIZE VALID INSTAGRAM ACCOUNT')
        raise SystemExit('BAD INITIALIZE VALID INSTAGRAM ACCOUNT')
    return cl


def check_instagram_account_validity(instagram_account):
    inst(f'Start checking instagram account {instagram_account.username}')
    try:
        cl = Client()

        # def process_challenge_code(message, bot):
        #     print(message.text)
        #     return message.text
        #
        # def challenge_code_handler(username, choice):
        #     bot = initialize_telegram_bot(1)
        #     telegram_user = get_telegram_user_by_instagram_account_username(username)
        #     message = PseudoTelegramChat(telegram_user.user_id)
        #     msg = bot.send_message(message.chat.id, 'Write ur code in next message')
        #     bot.register_next_step_handler(msg, process_challenge_code, bot)
        #     print(username, choice, bot)
        # cl.challenge_code_handler = challenge_code_handler
        if not os.path.exists(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json'):
            oss('Dump does not exists')
            cl.login(instagram_account.username, instagram_account.password, False)
        else:
            oss('Dump founded, trying load with this')
            cl.load_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
            cl.login(instagram_account.username, instagram_account.password)
        try:
            cl.get_timeline_feed()
            inst('Saving authorization dump')
            cl.dump_settings(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
            inst('Login done')
            return True
        except ClientLoginRequired as e:
            err(e)
            if os.path.exists(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json'):
                os.remove(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
                return check_instagram_account_validity(instagram_account)
            return False
        except LoginRequired as e:
            err(e)
            if os.path.exists(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json'):
                os.remove(f'{IG_DUMP_FOLDER_PATH}{instagram_account.username}.json')
                return check_instagram_account_validity(instagram_account)
            return False
        except Exception as e:
            err(e)
            return False
    except Exception as e:
        err(e)
    return False


class PseudoTelegramMessage:
    def __init__(self, user_id):
        self.id = user_id


class PseudoTelegramChat:
    def __init__(self, user_id):
        self.chat = PseudoTelegramMessage(user_id)
