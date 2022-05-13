from database.database import create_db_telegram_user, initialize_db, add_instagram_account, select_instagram_account, \
    get_selected_instagram_account, toggle_selected_active_instagram_account, set_selected_instagram_account_validity, \
    add_instagram_subscription, \
    select_instagram_subscription, toggle_selected_active_instagram_subscription, \
    get_selected_instagram_subscription
from functions.main import get_media
from markups import main_menu_markup, user_instagram_accounts_markup, \
    user_selected_instagram_account_markup, user_instagram_subscriptions_markup, \
    user_selected_instagram_subscription_markup
from misc import initialize_telegram_bot, get_username_from_url, check_instagram_account_validity

if __name__ == '__main__':
    initialize_db()
    bot = initialize_telegram_bot()


    @bot.message_handler(commands=['start'])
    def send_start(message):
        create_db_telegram_user(message.from_user.username, message.from_user.id)
        bot.send_message(message.chat.id, 'Welcome', reply_markup=main_menu_markup())


    @bot.callback_query_handler(func=lambda call: call.data == 'user_main_menu')
    def user_main_menu(call):
        bot.edit_message_text('Main menu', call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu_markup())


    @bot.callback_query_handler(func=lambda call: call.data == 'user_add_instagram_account')
    def user_add_instagram_account(call):
        msg = bot.edit_message_text('Write instagram username in next message', call.message.chat.id,
                                    call.message.message_id)
        bot.register_next_step_handler(msg, instagram_process_add_user_instagram_account, call)


    @bot.callback_query_handler(func=lambda call: call.data == 'user_instagram_accounts')
    def user_instagram_accounts(call):
        bot.edit_message_text('Instagram accounts', call.message.chat.id, call.message.message_id,
                              reply_markup=user_instagram_accounts_markup(call.from_user.id))


    @bot.callback_query_handler(func=lambda call: 'user_select_instagram_account:' in call.data)
    def user_select_instagram_account(call):
        username = call.data.partition('user_select_instagram_account:')[2]
        selected = select_instagram_account(username, call.from_user.id)
        bot.edit_message_text(
            f'Selected {selected.username}\n'
            f'Instagram status: {"Valid" if selected.is_valid else "Invalid"}\n'
            f'Last instagram validation: {selected.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}',
            call.message.chat.id, call.message.message_id,
            reply_markup=user_selected_instagram_account_markup(selected))


    @bot.callback_query_handler(func=lambda call: 'user_instagram_account:' in call.data)
    def user_instagram_account_change_active(call):
        selected = toggle_selected_active_instagram_account(call.from_user.id)
        bot.edit_message_text(
            f'Selected {selected.username}\n'
            f'Instagram status: {"Valid" if selected.is_valid else "Invalid"}\n'
            f'Last instagram validation: {selected.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}',
            call.message.chat.id, call.message.message_id,
            reply_markup=user_selected_instagram_account_markup(selected))


    @bot.callback_query_handler(func=lambda call: call.data == 'user_instagram_account_check_status')
    def user_instagram_account_check_status(call):
        selected = get_selected_instagram_account(call.from_user.id)
        is_valid = check_instagram_account_validity(selected)
        updated = set_selected_instagram_account_validity(call.from_user.id, is_valid)
        bot.edit_message_text(
            f'Selected {updated.username}\n'
            f'Instagram status: {"Valid" if updated.is_valid else "Invalid"}\n'
            f'Last instagram validation: {updated.last_validation_at.strftime("%Y-%m-%d %H:%M:%S")}',
            call.message.chat.id, call.message.message_id,
            reply_markup=user_selected_instagram_account_markup(updated))


    @bot.callback_query_handler(func=lambda call: call.data == 'user_instagram_subscriptions')
    def user_instagram_subscriptions(call):
        bot.edit_message_text('Your subscriptions', call.message.chat.id, call.message.message_id,
                              reply_markup=user_instagram_subscriptions_markup(call.message.chat.id))


    @bot.callback_query_handler(func=lambda call: call.data == 'user_add_instagram_subscription')
    def user_add_instagram_subscription(call):
        msg = bot.edit_message_text('Write target username or paste profile url', call.message.chat.id,
                                    call.message.message_id)
        bot.register_next_step_handler(msg, instagram_process_add_user_instagram_subscription, call)


    @bot.callback_query_handler(func=lambda call: 'user_select_instagram_subscription:' in call.data)
    def user_select_instagram_subscription(call):
        selected_instagram_subscription = call.data.partition('user_select_instagram_subscription:')[2]
        instagram_subscription = select_instagram_subscription(selected_instagram_subscription, call.message.chat.id)
        bot.edit_message_text(f'Selected: {instagram_subscription.username}', call.message.chat.id,
                              call.message.message_id,
                              reply_markup=user_selected_instagram_subscription_markup(instagram_subscription))


    @bot.callback_query_handler(func=lambda call: 'user_instagram_subscription:' in call.data)
    def user_instagram_subscription_change_active(call):
        instagram_subscription = toggle_selected_active_instagram_subscription(call.from_user.id)
        bot.edit_message_text(f'Selected: {instagram_subscription.username}',
                              call.message.chat.id, call.message.message_id,
                              reply_markup=user_selected_instagram_subscription_markup(instagram_subscription))


    @bot.callback_query_handler(func=lambda call: 'user_instagram_subscription_get:' in call.data)
    def user_instagram_subscription_get(call):
        target_for_get = call.data.partition('user_instagram_subscription_get:')[2]
        target_instagram_subscription = get_selected_instagram_subscription(call.message.chat.id)
        msg = bot.edit_message_text(f'Start collecting', call.message.chat.id, call.message.message_id)
        get_media(bot, call.message, target_instagram_subscription, target_for_get)
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        bot.send_message(call.message.chat.id, f'Collection complete\n\nSelected: {target_instagram_subscription.username}',
                         reply_markup=user_selected_instagram_subscription_markup(target_instagram_subscription))


    def instagram_process_add_user_instagram_subscription(message, call):
        target_username = get_username_from_url(message.text)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        add_instagram_subscription(target_username, call.message.chat.id)
        bot.edit_message_text('Your subscriptions', call.message.chat.id, call.message.message_id,
                              reply_markup=user_instagram_subscriptions_markup(call.message.chat.id))


    def instagram_process_add_user_instagram_account(message, call):
        username = message.text
        msg = bot.edit_message_text('Write instagram password in next message', call.message.chat.id,
                                    call.message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.register_next_step_handler(msg, instagram_process_add_user_instagram_account_password, call, username)


    def instagram_process_add_user_instagram_account_password(message, call, username):
        password = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        add_instagram_account(username, password, call.from_user.id)
        bot.edit_message_text('Account added', call.message.chat.id, call.message.message_id,
                              reply_markup=user_instagram_accounts_markup(call.from_user.id))


    #
    #
    # def start_scheduller():
    #     def thread_downloader(user):
    #         class IS:
    #             def __init__(self):
    #                 self.id = '216607409'
    #
    #         class M:
    #             def __init__(self):
    #                 self.chat = IS()
    #
    #         message = M()
    #         new_stories = get_new_stories(user, instagram_client)
    #         if len(new_stories) > 0:
    #             bot.send_message(message.chat.id,
    #                              f'User {user.username} have {len(new_stories)} new stories')
    #             grap_stories(bot, message, user.username, instagram_client, amount=len(new_stories))
    #
    #         new_posts = get_new_posts(user, instagram_client)
    #         if len(new_posts) > 0:
    #             bot.send_message(message.chat.id, f'User {user.username} have {len(new_posts)} new posts')
    #             grap_posts(bot, message, user.username, instagram_client, amount=len(new_posts))
    #
    #         new_highlights = get_new_highlights(user, instagram_client)
    #         if len(new_highlights) > 0:
    #             bot.send_message(message.chat.id,
    #                              f'User {user.username} have {len(new_highlights)} new highlights')
    #             grap_highlights(bot, message, user.username, instagram_client)
    #
    #     def main_scheduller_thread():
    #         global is_now_downloading
    #         with closing(initialize_database_connection()) as connection:
    #             with closing(connection.cursor()) as cursor:
    #                 is_now_downloading = True
    #                 rows = cursor.execute("SELECT * FROM TRACKED_USERS").fetchall()
    #                 for row in rows:
    #                     user = TrackedUsers(*row)
    #                     t = threading.Thread(target=thread_downloader, args=(user,))
    #                     t.start()
    #                     t.join()
    #                 is_now_downloading = False
    #
    #     scheduler = BlockingScheduler()
    #     scheduler.add_job(main_scheduller_thread, 'interval', hours=1)
    #     scheduler.start()
    #
    #
    # t1 = threading.Thread(target=start_scheduller)
    # t1.start()

    bot.infinity_polling()
