from bot.markups.markups import user_selected_instagram_user_markup
from database.database import InstagramPost
from database.get import get_active_instagram_account_by_instagram_user
from database.set import add_instagram_post_to_instagram_user, update_instagram_user_active_instagram_account_by_id
from instagram.downloads import download_and_send_photo, download_and_send_video, download_and_send_album
from utils.misc import BColors, divider, create_folder_by_username, inst, err


def grap_posts(bot, message, instagram_user, cl, amount=0):
    instagram_user_active_instagram_account = get_active_instagram_account_by_instagram_user(instagram_user)
    try:
        user_id = int(cl.user_id_from_username(instagram_user.username))
        inst(f'User id: {user_id}')

        inst(f'Start collecting {instagram_user.username} {BColors.OKBLUE}posts{BColors.ENDC}')
        posts = cl.user_medias(user_id, amount)
        posts.reverse()
        inst('Posts collecting complete')

        divider()

        inst(f'Founded {len(posts)} {BColors.OKCYAN}posts{BColors.ENDC}')
        if len(posts) > 0:
            create_folder_by_username(instagram_user.username)
            for post in posts:
                download_post(bot, post, message, instagram_user, cl)

        inst(f'Grepping {BColors.OKCYAN}posts{BColors.ENDC} complete')
        bot.send_message(message.chat.id,
                         f'Collection complete\n\nSelected: {instagram_user.username}',
                         reply_markup=user_selected_instagram_user_markup(instagram_user))
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
    finally:
        pass
        # update_instagram_user_active_instagram_account_by_id(instagram_user_active_instagram_account.id, False)


def download_post(bot, post, message, instagram_user, cl):
    inst(f'Start downloading and sending {instagram_user.username} post')
    sent = False
    if post.media_type == 1:
        sent = download_and_send_photo(bot, post, message, instagram_user.username, cl)
    if post.media_type == 2:
        sent = download_and_send_video(bot, post, message, instagram_user.username, cl)
    if post.media_type == 8:
        sent = download_and_send_album(bot, post, message, instagram_user.username, cl)
    if sent:
        add_instagram_post_to_instagram_user(post, message.chat.id)


def get_posts_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    posts = instagram_client.user_medias(user_id)
    arr = []
    for post in posts:
        arr.append(int(post.pk))
    return arr


def get_new_posts(instagram_user, instagram_client):
    posts = get_posts_list(instagram_user.username, instagram_client)
    instagram_user_posts = InstagramPost.select(InstagramPost.pk).execute()
    instagram_user_posts_filtered = [int(post.pk) for post in instagram_user_posts]
    return list(set(posts) - set(instagram_user_posts_filtered))
