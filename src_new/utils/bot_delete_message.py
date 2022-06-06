from telebot import TeleBot
from telebot.types import Message


def bdm(bot: TeleBot, message: Message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
