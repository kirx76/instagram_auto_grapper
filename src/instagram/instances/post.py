import time

from instagrapi.exceptions import PleaseWaitFewMinutes

from bot.markups.markups import user_selected_instagram_user_markup
from database.database import InstagramPost
from database.set import add_instagram_post_to_instagram_user
from instagram.downloads import download_and_send_photo, download_and_send_video, download_and_send_album
from utils.misc import BColors, divider, create_folder_by_username, inst, err, oss


def grap_posts(bot, message, instagram_user, cl, pks):
    try:
        user_id = int(cl.user_id_from_username(instagram_user.username))
        inst(f'User id: {user_id}')

        divider()

        inst(f'Founded {len(pks)} {BColors.OKCYAN}posts{BColors.ENDC}')
        if len(pks) > 0:
            create_folder_by_username(instagram_user.username)
            for post in pks:
                download_post(bot, post, message, instagram_user, cl)

        inst(f'Grepping {BColors.OKCYAN}posts{BColors.ENDC} complete')
        bot.send_message(message.chat.id,
                         f'Collection complete\n\nSelected: {instagram_user.username}',
                         reply_markup=user_selected_instagram_user_markup(instagram_user))
    except PleaseWaitFewMinutes as e:
        err(e)
        oss('Sleep 300 s')
        time.sleep(300)
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
    finally:
        pass


def download_post(bot, post, message, instagram_user, cl):
    inst(f'Start downloading and sending {instagram_user.username} post')
    sent = False
    files = None
    if post.media_type == 1:
        sent, files = download_and_send_photo(bot, post, message, instagram_user.username, cl)
    if post.media_type == 2:
        sent, files = download_and_send_video(bot, post, message, instagram_user.username, cl)
    if post.media_type == 8:
        sent, files = download_and_send_album(bot, post, message, instagram_user.username, cl)
    if sent:
        add_instagram_post_to_instagram_user(post, message.chat.id, files)


def get_posts_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    return instagram_client.user_medias(user_id)


def get_new_posts(instagram_user, instagram_client):
    posts = get_posts_list(instagram_user.username, instagram_client)
    pre_instagram_user_posts = InstagramPost.select().where(InstagramPost.user == instagram_user.pk).execute()
    instagram_user_posts_pks = [int(y.pk) for y in pre_instagram_user_posts]
    posts_pks = [int(post.pk) for post in posts]
    filtered_list_of_posts_pks = list(set(posts_pks) - set(instagram_user_posts_pks))
    done_posts = []
    for pk in filtered_list_of_posts_pks:
        done_posts += ([x for x in posts if int(x.pk) == pk])

    return done_posts
