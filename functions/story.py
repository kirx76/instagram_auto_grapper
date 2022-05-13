from database.database import InstagramStory, add_instagram_story_to_instagram_subscription
from functions.downloads import download_and_send_story
from misc import BColors, divider, create_folder_by_username, inst, err


def grap_stories(bot, message, instagram_subscription, cl, amount=0):
    user_id = int(cl.user_id_from_username(instagram_subscription.username))
    inst(f'User id: {user_id}')

    inst(f'Start collecting {instagram_subscription.username} {BColors.OKBLUE}stories{BColors.ENDC}')
    stories = cl.user_stories(user_id, amount)
    stories.reverse()
    inst('Stories collecting complete')

    divider()

    inst(f'Founded {len(stories)} {BColors.OKCYAN}stories{BColors.ENDC}')
    if len(stories) > 0:
        create_folder_by_username(instagram_subscription.username)
        for story in stories:
            download_story(bot, story, message, instagram_subscription, cl)

    inst(f'Grepping {BColors.OKCYAN}stories{BColors.ENDC} complete')


def download_story(bot, story, message, instagram_subscription, cl):
    inst(f'Start downloading and sending {instagram_subscription.username} story')
    sent = download_and_send_story(bot, story, message, instagram_subscription.username, cl)
    if sent:
        add_instagram_story_to_instagram_subscription(instagram_subscription, story.pk, None,
                                                      story.taken_at)


def get_stories_list(username, instagram_client):
    user_id = int(instagram_client.user_id_from_username(username))
    stories = instagram_client.user_stories(user_id)
    arr = []
    for story in stories:
        arr.append(int(story.pk))
    return arr


def get_new_stories(instagram_subscription, instagram_client):
    last_story = instagram_subscription.stories.select().order_by(InstagramStory.id.desc()).first()
    stories = get_stories_list(instagram_subscription.username, instagram_client)
    if last_story:
        try:
            index = stories.index(int(last_story.pk))
            return stories[:index]
        except Exception as e:
            err(e)
            return stories
    else:
        return stories
