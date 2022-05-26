import threading

from telebot import apihelper

from bot.admin_logic import admin_instagram_accounts, admin_select_instagram_account, admin_restore_instagram_account
from bot.instagram_account_logic import user_add_instagram_account, user_instagram_accounts, \
    user_select_instagram_account, user_instagram_account_change_active, user_instagram_account_check_status, \
    user_delete_instagram_account
from bot.instagram_user_logic import user_instagram_users, user_add_instagram_user, \
    user_select_instagram_user, user_instagram_user_change_active, user_instagram_user_get, user_instagram_user_get_sent
from bot.main import send_start, user_main_menu, antispam_func, AdminFilter, main_scheduler, DownloadingFilter, \
    BannedFilter, UsualFilter, NormalFilter, VIPFilter, characters_page_callback
from database.database import initialize_db
from database.set import clean_all_instagram_account_works
from utils.misc import initialize_telegram_bot

initialize_db()
apihelper.ENABLE_MIDDLEWARE = True
bot = initialize_telegram_bot(threads=5)


def register_main_handlers():
    bot.register_message_handler(send_start, commands=['start'], banned=False, pass_bot=True)
    bot.register_callback_query_handler(user_main_menu, func=lambda call: call.data == 'user_main_menu', banned=False,
                                        pass_bot=True)


def register_instagram_account_handlers():
    bot.register_callback_query_handler(user_add_instagram_account,
                                        downloading=False, banned=False,
                                        func=lambda call: call.data == 'user_add_instagram_account', pass_bot=True)
    bot.register_callback_query_handler(user_delete_instagram_account,
                                        downloading=False, banned=False,
                                        func=lambda call: call.data == 'user_delete_instagram_account', pass_bot=True)
    bot.register_callback_query_handler(user_instagram_accounts, banned=False,
                                        func=lambda call: call.data == 'user_instagram_accounts', pass_bot=True)
    bot.register_callback_query_handler(user_select_instagram_account,
                                        downloading=False, banned=False,
                                        func=lambda call: 'user_select_instagram_account:' in call.data, pass_bot=True)
    bot.register_callback_query_handler(user_instagram_account_change_active,
                                        downloading=False, banned=False,
                                        func=lambda call: 'user_instagram_account:' in call.data, pass_bot=True)
    bot.register_callback_query_handler(user_instagram_account_check_status,
                                        downloading=False, banned=False,
                                        func=lambda call: call.data == 'user_instagram_account_check_status',
                                        pass_bot=True)


def register_instagram_user_handlers():
    bot.register_callback_query_handler(user_instagram_users, banned=False,
                                        func=lambda call: call.data == 'user_instagram_users', pass_bot=True)
    bot.register_callback_query_handler(user_add_instagram_user,
                                        downloading=False, banned=False,
                                        func=lambda call: call.data == 'user_add_instagram_user', pass_bot=True)
    bot.register_callback_query_handler(user_select_instagram_user, banned=False, downloading=False,
                                        func=lambda call: 'user_select_instagram_user:' in call.data,
                                        pass_bot=True)
    bot.register_callback_query_handler(user_instagram_user_change_active,
                                        downloading=False, banned=False,
                                        func=lambda call: 'user_instagram_user:' in call.data, pass_bot=True)
    bot.register_callback_query_handler(user_instagram_user_get, banned=False, downloading=False,
                                        func=lambda call: 'user_instagram_user_get:' in call.data,
                                        pass_bot=True)
    bot.register_callback_query_handler(user_instagram_user_get_sent, banned=False, downloading=False,
                                        func=lambda call: 'user_instagram_user_get_sent:' in call.data,
                                        pass_bot=True)
    bot.register_callback_query_handler(characters_page_callback, banned=False, downloading=False,
                                        func=lambda call: 'user_instagram_user_page:' in call.data, pass_bot=True)


def register_admin_handlers():
    bot.register_callback_query_handler(admin_instagram_accounts,
                                        downloading=False, banned=False, admin=True,
                                        func=lambda call: call.data == 'admin_instagram_accounts',
                                        pass_bot=True)
    bot.register_callback_query_handler(admin_restore_instagram_account,
                                        downloading=False, banned=False, admin=True,
                                        func=lambda call: call.data == 'admin_restore_instagram_account',
                                        pass_bot=True)
    bot.register_callback_query_handler(admin_select_instagram_account,
                                        downloading=False, banned=False, admin=True,
                                        func=lambda call: 'admin_select_instagram_account:' in call.data,
                                        pass_bot=True)


def register_middlewares():
    bot.register_middleware_handler(antispam_func, update_types=['message'])


def register_custom_filters():
    bot.add_custom_filter(DownloadingFilter(bot))
    bot.add_custom_filter(AdminFilter())
    bot.add_custom_filter(UsualFilter())
    bot.add_custom_filter(NormalFilter())
    bot.add_custom_filter(VIPFilter())
    bot.add_custom_filter(BannedFilter())


def register_grapper_thread():
    clean_all_instagram_account_works()
    grapper_thread = threading.Thread(target=main_scheduler, args=(bot,))
    grapper_thread.start()


register_instagram_account_handlers()
register_instagram_user_handlers()
register_main_handlers()
register_admin_handlers()
register_middlewares()
register_custom_filters()
register_grapper_thread()


def run():
    bot.infinity_polling()

# test cicd
if __name__ == '__main__':
    run()
