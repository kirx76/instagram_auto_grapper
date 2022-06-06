from telebot import apihelper

from bot.functions import send_start, user_iaccounts, user_add_iaccount, user_iaccount_menu, \
    user_selected_iaccount_menu, user_iusers, user_add_iuser
from bot.main import initialize_bot
from database.functions import initialize_db


def register_main_handlers():
    bot.register_message_handler(send_start, commands=['start'], pass_bot=True)


def register_iaccount_handlers():
    bot.register_callback_query_handler(user_iaccounts, func=lambda call: call.data == 'user_iaccounts', pass_bot=True)
    bot.register_callback_query_handler(user_add_iaccount, func=lambda call: call.data == 'user_add_iaccount', pass_bot=True)
    bot.register_callback_query_handler(user_iaccount_menu, func=lambda call: 'user_iaccount_menu:' in call.data, pass_bot=True)
    bot.register_callback_query_handler(user_selected_iaccount_menu, func=lambda call: 'user_selected_iaccount_menu:' in call.data, pass_bot=True)


def register_iuser_handlers():
    bot.register_callback_query_handler(user_iusers, func=lambda call: call.data == 'user_iusers', pass_bot=True)
    bot.register_callback_query_handler(user_add_iuser, func=lambda call: call.data == 'user_add_iuser', pass_bot=True)



def main():
    bot.infinity_polling()


if __name__ == '__main__':
    apihelper.ENABLE_MIDDLEWARE = True
    initialize_db()
    bot = initialize_bot(threads=5)
    register_main_handlers()
    register_iaccount_handlers()
    register_iuser_handlers()

    main()
