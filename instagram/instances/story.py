from database.database import InstagramStory
from database.set import add_instagram_story_to_instagram_user
from instagram.downloads import download_and_send_story
from utils.misc import BColors, divider, create_folder_by_username, inst, err


def grap_stories(bot, message, instagram_user, cl, amount=0):
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
    last_story = instagram_user.stories.select().order_by(InstagramStory.id.desc()).first()
    stories = get_stories_list(instagram_user.username, instagram_client)
    if last_story:
        try:
            index = stories.index(int(last_story.pk))
            return stories[:index]
        except Exception as e:
            err(e)
            return stories
    else:
        return stories
