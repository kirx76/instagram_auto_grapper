from database.database import get_telegram_user_active_instagram_account
from functions.highlight import get_new_highlights, grap_highlights
from functions.post import get_new_posts, grap_posts
from functions.story import get_new_stories, grap_stories
from misc import initialize_valid_instagram_account, err, inst


def get_media(bot, message, instagram_subscription, target):
    try:
        inst(f'Current target: {instagram_subscription.username}')
        active_instagram_account = get_telegram_user_active_instagram_account(message.chat.id)
        valid_instagram_account = initialize_valid_instagram_account(active_instagram_account)

        if target == 'posts':
            new_posts = get_new_posts(instagram_subscription, valid_instagram_account)
            if len(new_posts) > 0:
                grap_posts(bot, message, instagram_subscription, valid_instagram_account, amount=len(new_posts))

        if target == 'stories':
            new_stories = get_new_stories(instagram_subscription, valid_instagram_account)
            if len(new_stories) > 0:
                grap_stories(bot, message, instagram_subscription, valid_instagram_account, amount=len(new_stories))

        if target == 'highlights':
            new_highlights = get_new_highlights(instagram_subscription, valid_instagram_account)
            if len(new_highlights) > 0:
                grap_highlights(bot, message, instagram_subscription, valid_instagram_account)
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
