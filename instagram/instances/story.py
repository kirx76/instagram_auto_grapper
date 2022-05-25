from instagrapi.types import Story

from bot.markups.markups import user_selected_instagram_user_markup
from database.database import InstagramStory
from database.set import add_instagram_story_to_instagram_user
from instagram.downloads import download_and_send_story
from utils.misc import BColors, divider, create_folder_by_username, inst, err


def grap_stories(bot, message, instagram_user, cl, pks):
    try:
        user_id = int(cl.user_id_from_username(instagram_user.username))
        inst(f'User id: {user_id}')

        divider()

        inst(f'Founded {len(pks)} {BColors.OKCYAN}stories{BColors.ENDC}')
        if len(pks) > 0:
            create_folder_by_username(instagram_user.username)
            for story in pks:
                download_story(bot, story, message, instagram_user, cl)

        inst(f'Grepping {BColors.OKCYAN}stories{BColors.ENDC} complete')
        bot.send_message(message.chat.id,
                         f'Collection complete\n\nSelected: {instagram_user.username}',
                         reply_markup=user_selected_instagram_user_markup(instagram_user))
    except Exception as e:
        err(e)
        bot.send_message(message.chat.id, e)
    finally:
        pass


def download_story(bot, story, message, instagram_user, cl):
    inst(f'Start downloading and sending {instagram_user.username} story')
    sent, files = download_and_send_story(bot, story, message, instagram_user.username, cl)
    if sent:
        add_instagram_story_to_instagram_user(story, message.chat.id, files)


def get_stories_list(username, instagram_client) -> list[Story]:
    user_id = int(instagram_client.user_id_from_username(username))
    return instagram_client.user_stories(user_id)


def get_new_stories(instagram_user, instagram_client):
    stories = get_stories_list(instagram_user.username, instagram_client)
    pre_instagram_user_stories = InstagramStory.select().where(InstagramStory.user == instagram_user.pk).execute()
    instagram_user_stories_pks = [int(y.pk) for y in pre_instagram_user_stories]
    stories_pks = [int(story.pk) for story in stories]
    filtered_list_of_stories_pks = list(set(stories_pks) - set(instagram_user_stories_pks))
    done_stories = []
    for pk in filtered_list_of_stories_pks:
        done_stories += ([x for x in stories if int(x.pk) == pk])

    return done_stories
