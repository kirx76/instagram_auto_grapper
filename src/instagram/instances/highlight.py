import time

from instagrapi.exceptions import PleaseWaitFewMinutes

from bot.markups.markups import iu_i_menu_markup
from database.database import InstagramHighlight
from database.set import add_instagram_highlight_to_instagram_user
from instagram.downloads import download_and_send_highlight
from utils.misc import BColors, divider, create_folder_by_username, err, inst, oss


def grap_highlights(bot, message, instagram_user, cl, pks):
    try:
        user_id = int(cl.user_id_from_username(instagram_user.username))
        inst(f'User id: {user_id}')

        divider()

        inst(f'Founded {len(pks)} {BColors.OKCYAN}highlights{BColors.ENDC}')
        if len(pks) > 0:
            create_folder_by_username(instagram_user.username)
            for index, highlight in enumerate(pks):
                inst(f'Highlight #{index + 1} of {len(pks)}')
                download_highlight(bot, highlight, message, instagram_user, cl)

        inst(f'Grepping {BColors.OKCYAN}highlights{BColors.ENDC} complete')
        bot.send_photo(chat_id=message.chat.id, photo=instagram_user.profile_pic_location,
                       reply_markup=iu_i_menu_markup(instagram_user),
                       caption='Collection complete')
    except PleaseWaitFewMinutes as e:
        err(e)
        oss('Sleep 300 s')
        time.sleep(300)
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
    finally:
        pass


def download_highlight(bot, highlight_pk, message, instagram_user, cl):
    inst(f'Start downloading and sending {instagram_user.username} highlight')
    highlight = cl.story_info(highlight_pk)
    sent, files = download_and_send_highlight(bot, highlight, message, instagram_user.username, cl)
    if sent:
        add_instagram_highlight_to_instagram_user(highlight, message.chat.id, files)


def get_highlights_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    highlights = instagram_client.user_highlights(user_id)
    medias = []
    for highlight in highlights:
        medias += instagram_client.highlight_info(highlight.pk).media_ids
    return medias


def get_new_highlights(instagram_user, instagram_client):
    highlights = get_highlights_list(instagram_user.username, instagram_client)
    instagram_user_highlights = InstagramHighlight.select().where(
        InstagramHighlight.user == instagram_user.pk).execute()
    instagram_user_highlights_filtered = [int(highlight.pk) for highlight in instagram_user_highlights]
    return list(set(highlights) - set(instagram_user_highlights_filtered))
