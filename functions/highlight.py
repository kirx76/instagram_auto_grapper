from database.database import InstagramHighlight, add_instagram_highlight_to_instagram_subscription
from functions.downloads import download_and_send_highlight
from misc import BColors, divider, create_folder_by_username, err, inst


def grap_highlights(bot, message, instagram_subscription, cl):
    user_id = int(cl.user_id_from_username(instagram_subscription.username))
    inst(f'User id: {user_id}')

    inst(f'Start collecting {instagram_subscription.username} {BColors.OKBLUE}highlights{BColors.ENDC}')

    highlights = get_new_highlights(instagram_subscription, cl)
    highlights.reverse()
    inst('Highlights collecting complete')

    divider()

    inst(f'Founded {len(highlights)} {BColors.OKCYAN}highlights{BColors.ENDC}')
    if len(highlights) > 0:
        create_folder_by_username(instagram_subscription.username)
        for highlight in highlights:
            download_highlight(bot, highlight, message, instagram_subscription, cl)

    inst(f'Grepping {BColors.OKCYAN}highlights{BColors.ENDC} complete')


def download_highlight(bot, highlight_pk, message, instagram_subscription, cl):
    inst(f'Start downloading and sending {instagram_subscription.username} highlight')
    highlight = cl.story_info(highlight_pk)
    sent = download_and_send_highlight(bot, highlight, message, instagram_subscription.username, cl)
    if sent:
        add_instagram_highlight_to_instagram_subscription(instagram_subscription, highlight.pk, None,
                                                          highlight.taken_at)


def get_highlights_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    highlights = instagram_client.user_highlights(user_id)
    medias = []
    for highlight in highlights:
        medias += instagram_client.highlight_info(highlight.pk).media_ids
    return medias


def get_new_highlights(instagram_subscription, instagram_client):
    last_highlight = instagram_subscription.highlights.select().order_by(InstagramHighlight.id.desc()).first()
    highlights = get_highlights_list(instagram_subscription.username, instagram_client)
    if last_highlight:
        try:
            index = highlights.index(int(last_highlight.pk))
            return highlights[:index]
        except Exception as e:
            err(e)
            return highlights
    else:
        return highlights
