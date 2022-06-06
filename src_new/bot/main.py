import os

import telebot
from dotenv import load_dotenv

load_dotenv()


def initialize_bot(threads=5):
    return telebot.TeleBot(os.environ.get("TG_BOT_TOKEN"), parse_mode='HTML', num_threads=threads)
