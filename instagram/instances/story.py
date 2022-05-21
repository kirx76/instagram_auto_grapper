from bot.markups.markups import user_selected_instagram_user_markup
from database.database import InstagramStory
from database.get import get_active_instagram_account_by_instagram_user
from database.set import add_instagram_story_to_instagram_user, update_instagram_user_active_instagram_account_by_id
from instagram.downloads import download_and_send_story
from utils.misc import BColors, divider, create_folder_by_username, inst, err


def grap_stories(bot, message, instagram_user, cl, amount=0):
    instagram_user_active_instagram_account = get_active_instagram_account_by_instagram_user(instagram_user)
    try:
        user_id = int(cl.user_id_from_username(instagram_user.username))
        inst(f'User id: {user_id}')

        inst(f'Start collecting {instagram_user.username} {BColors.OKBLUE}stories{BColors.ENDC}')
        stories = cl.user_stories(user_id, amount)
        stories.reverse()
        inst('Stories collecting complete')

        divider()

        inst(f'Founded {len(stories)} {BColors.OKCYAN}stories{BColors.ENDC}')
        if len(stories) > 0:
            create_folder_by_username(instagram_user.username)
            for story in stories:
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
        # update_instagram_user_active_instagram_account_by_id(instagram_user_active_instagram_account.id, False)


def download_story(bot, story, message, instagram_user, cl):
    inst(f'Start downloading and sending {instagram_user.username} story')
    sent = download_and_send_story(bot, story, message, instagram_user.username, cl)
    if sent:
        add_instagram_story_to_instagram_user(story, message.chat.id)


def get_stories_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    stories = instagram_client.user_stories(user_id)
    arr = []
    for story in stories:
        arr.append(int(story.pk))
    return arr


def get_new_stories(instagram_user, instagram_client):
    stories = get_stories_list(instagram_user.username, instagram_client)
    instagram_user_stories = InstagramStory.select(InstagramStory.pk).execute()
    instagram_user_stories_filtered = [int(story.pk) for story in instagram_user_stories]
    return list(set(stories) - set(instagram_user_stories_filtered))
