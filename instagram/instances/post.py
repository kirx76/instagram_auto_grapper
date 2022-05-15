from database.database import InstagramPost, add_instagram_post_to_instagram_subscription
from instagram.downloads import download_and_send_photo, download_and_send_video, download_and_send_album
from utils.misc import BColors, divider, create_folder_by_username, inst, err


def grap_posts(bot, message, instagram_subscription, cl, amount=0):
    user_id = int(cl.user_id_from_username(instagram_subscription.username))
    inst(f'User id: {user_id}')

    inst(f'Start collecting {instagram_subscription.username} {BColors.OKBLUE}posts{BColors.ENDC}')
    posts = cl.user_medias(user_id, amount)
    posts.reverse()
    inst('Posts collecting complete')

    divider()

    inst(f'Founded {len(posts)} {BColors.OKCYAN}posts{BColors.ENDC}')
    if len(posts) > 0:
        create_folder_by_username(instagram_subscription.username)
        for post in posts:
            download_post(bot, post, message, instagram_subscription, cl)

    inst(f'Grepping {BColors.OKCYAN}posts{BColors.ENDC} complete')


def download_post(bot, post, message, instagram_subscription, cl):
    inst(f'Start downloading and sending {instagram_subscription.username} post')
    sent = False
    if post.media_type == 1:
        sent = download_and_send_photo(bot, post, message, instagram_subscription.username, cl)
    if post.media_type == 2:
        sent = download_and_send_video(bot, post, message, instagram_subscription.username, cl)
    if post.media_type == 8:
        sent = download_and_send_album(bot, post, message, instagram_subscription.username, cl)
    if sent:
        add_instagram_post_to_instagram_subscription(instagram_subscription, post)


def get_posts_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    posts = instagram_client.user_medias(user_id)
    arr = []
    for post in posts:
        arr.append(int(post.pk))
    return arr


def get_new_posts(instagram_subscription, instagram_client):
    last_post = instagram_subscription.posts.select().order_by(InstagramPost.id.desc()).first()
    posts = get_posts_list(instagram_subscription.username, instagram_client)
    if last_post:
        try:
            index = posts.index(int(last_post.pk))
            return posts[:index]
        except Exception as e:
            err(e)
            return posts
    else:
        return posts
