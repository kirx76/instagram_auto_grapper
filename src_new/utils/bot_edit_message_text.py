from typing import Optional

from telebot import TeleBot, REPLY_MARKUP_TYPES
from telebot.types import Message


def bemt(bot: TeleBot, message: Message, text: str, reply_markup: Optional[REPLY_MARKUP_TYPES] = None):
    return bot.edit_message_text(text, chat_id=message.chat.id, message_id=message.message_id,
                                 reply_markup=reply_markup)
