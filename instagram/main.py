from bot.main import default_downloader_thread_starter
from database.get import get_telegram_user_active_instagram_account
from instagram.instances.highlight import get_new_highlights, grap_highlights
from instagram.instances.post import get_new_posts, grap_posts
from instagram.instances.story import get_new_stories, grap_stories
from utils.misc import initialize_valid_instagram_account, err, inst


def get_media(bot, message, instagram_user, target):
    try:
        inst(f'Current target: {instagram_user.username}')
        active_instagram_account = get_telegram_user_active_instagram_account(message.chat.id)
        valid_instagram_account = initialize_valid_instagram_account(active_instagram_account, bot, message.chat.id)

        if target == 'posts':
            new_posts = get_new_posts(instagram_user, valid_instagram_account)
            if len(new_posts) > 0:
                default_downloader_thread_starter(grap_posts, bot, message, instagram_user, valid_instagram_account,
                                                  pks=new_posts)

        if target == 'stories':
            new_stories = get_new_stories(instagram_user, valid_instagram_account)
            if len(new_stories) > 0:
                default_downloader_thread_starter(grap_stories, bot, message, instagram_user, valid_instagram_account,
                                                  pks=new_stories)

        if target == 'highlights':
            new_highlights = get_new_highlights(instagram_user, valid_instagram_account)
            if len(new_highlights) > 0:
                default_downloader_thread_starter(grap_highlights, bot, message, instagram_user,
                                                  valid_instagram_account,
                                                  pks=new_highlights)
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
