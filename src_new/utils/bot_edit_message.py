from typing import Optional

from telebot import TeleBot, REPLY_MARKUP_TYPES
from telebot.types import Message, InputMediaPhoto


def bemt(bot: TeleBot, message: Message, text: str, reply_markup: Optional[REPLY_MARKUP_TYPES] = None):
    return bot.edit_message_text(text, chat_id=message.chat.id, message_id=message.message_id,
                                 reply_markup=reply_markup)


def bemp(bot: TeleBot, message: Message, file_id: str, caption: str, reply_markup: Optional[REPLY_MARKUP_TYPES] = None):
    return bot.edit_message_media(media=InputMediaPhoto(file_id, caption=caption), chat_id=message.chat.id,
                                  message_id=message.message_id, reply_markup=reply_markup)


def bsm(bot: TeleBot, chat_id, text: str, reply_markup: Optional[REPLY_MARKUP_TYPES] = None):
    return bot.send_message(chat_id, text, reply_markup=reply_markup)


def bsp(bot: TeleBot, chat_id, file_id: str, caption: str, reply_markup: Optional[REPLY_MARKUP_TYPES] = None):
    return bot.send_photo(chat_id, file_id, caption=caption, reply_markup=reply_markup)
