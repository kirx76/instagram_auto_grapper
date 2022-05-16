from database.database import InstagramHighlight
from database.set import add_instagram_highlight_to_instagram_user
from instagram.downloads import download_and_send_highlight
from utils.misc import BColors, divider, create_folder_by_username, err, inst


def grap_highlights(bot, message, instagram_user, cl):
    user_id = int(cl.user_id_from_username(instagram_user.username))
    inst(f'User id: {user_id}')

    inst(f'Start collecting {instagram_user.username} {BColors.OKBLUE}highlights{BColors.ENDC}')

    highlights = get_new_highlights(instagram_user, cl)
    highlights.reverse()
    inst('Highlights collecting complete')

    divider()

    inst(f'Founded {len(highlights)} {BColors.OKCYAN}highlights{BColors.ENDC}')
    if len(highlights) > 0:
        create_folder_by_username(instagram_user.username)
        for highlight in highlights:
            download_highlight(bot, highlight, message, instagram_user, cl)

    inst(f'Grepping {BColors.OKCYAN}highlights{BColors.ENDC} complete')


def download_highlight(bot, highlight_pk, message, instagram_user, cl):
    inst(f'Start downloading and sending {instagram_user.username} highlight')
    highlight = cl.story_info(highlight_pk)
    sent = download_and_send_highlight(bot, highlight, message, instagram_user.username, cl)
    if sent:
        add_instagram_highlight_to_instagram_user(highlight, message.chat.id)


def get_highlights_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    highlights = instagram_client.user_highlights(user_id)
    medias = []
    for highlight in highlights:
        medias += instagram_client.highlight_info(highlight.pk).media_ids
    return medias


def get_new_highlights(instagram_user, instagram_client):
    last_highlight = instagram_user.highlights.select().order_by(InstagramHighlight.id.desc()).first()
    highlights = get_highlights_list(instagram_user.username, instagram_client)
    if last_highlight:
        try:
            index = highlights.index(int(last_highlight.pk))
            return highlights[:index]
        except Exception as e:
            err(e)
            return highlights
    else:
        return highlights
