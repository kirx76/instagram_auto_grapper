import datetime

import requests

from src.database.database import InstagramAccount, InstagramStory, InstagramPostResource, InstagramPost, InstagramUser, \
    TelegramUser, InstagramHighlight
from src.database.get import get_current_telegram_user, get_selected_instagram_user, get_selected_instagram_account, \
    get_active_instagram_account_by_telegram_user_id
from src.utils.misc import dbm, initialize_valid_instagram_account, caption_text_to_db, AWS, \
    create_folder_by_username


def add_instagram_user(username, user_id, bot, telegram_user_id) -> InstagramUser:
    telegram_user = get_current_telegram_user(user_id)
    active_instagram_account = get_active_instagram_account_by_telegram_user_id(user_id)
    instagram_account = initialize_valid_instagram_account(active_instagram_account, bot, telegram_user_id)
    instagram_user_info = instagram_account.user_info_by_username(username)
    dbm('Adding instagram account')
    return create_or_get_instagram_user(instagram_user_info, telegram_user)


def delete_selected_instagram_account(user_id):
    selected = get_selected_instagram_account(user_id)
    TelegramUser.update({TelegramUser.selected_instagram_account: None}).where(
        TelegramUser.user_id == user_id).execute()
    InstagramAccount.update(
        {InstagramAccount.is_deleted: True, InstagramAccount.is_active: False, InstagramAccount.is_valid: False}).where(
        InstagramAccount.id == selected.id).execute()
    dbm('Deleting selected instagram account')


def add_instagram_account(username, password, user_id) -> InstagramAccount:
    telegram_user = get_current_telegram_user(user_id)
    ia, created = InstagramAccount.get_or_create(username=username, password=password, added_by=telegram_user.id)
    if created:
        dbm(f'Instagram account {username} created')
    else:
        dbm(f'Instagram account {username} already exists')
    return ia


def restore_selected_instagram_account(user_id):
    selected = get_selected_instagram_account(user_id)
    InstagramAccount.update({InstagramAccount.is_deleted: False}).where(InstagramAccount.id == selected.id).execute()
    dbm('Restoring selected instagram account')
    return get_selected_instagram_account(user_id)


def set_selected_instagram_account_validity(user_id, state):
    ia = get_selected_instagram_account(user_id)
    dbm('Change selected instagram account validity')
    ia.is_valid = state
    ia.last_validation_at = datetime.datetime.now()
    ia.save()
    return ia


def create_db_telegram_user(username, user_id):
    user, created = TelegramUser.get_or_create(username=username, user_id=user_id)
    if created:
        dbm(f'User {username} created')
    else:
        dbm(f'User {username} already exists')
    return user


def disable_all_instagram_accounts_for_telegram_user(telegram_user_id):
    dbm('Disable all telegram user instagram accounts active statuses')
    telegram_user = get_current_telegram_user(telegram_user_id)
    InstagramAccount.update({InstagramAccount.is_active: False}).where(
        InstagramAccount.added_by == telegram_user.id).execute()


def toggle_selected_active_instagram_account(user_id):
    iaa = get_selected_instagram_account(user_id)
    disable_all_instagram_accounts_for_telegram_user(user_id)
    InstagramAccount.update({InstagramAccount.is_active: False if iaa.is_active else True}).where(
        InstagramAccount.id == iaa.id).execute()
    dbm('Toggled selected instagram account active')
    return get_selected_instagram_account(user_id)


def toggle_selected_active_instagram_user(user_id):
    isub = get_selected_instagram_user(user_id)
    dbm('Toggled selected instagram user activity')
    isub.enabled = False if isub.enabled else True
    isub.save()
    return isub


def add_instagram_post_to_instagram_user(post: InstagramPost, telegram_user_id, files) -> InstagramPost:
    telegram_user = get_current_telegram_user(telegram_user_id)
    create_or_get_instagram_user(post.user, telegram_user)
    exists_post = InstagramPost.get_or_none(InstagramPost.pk == post.pk)
    file_id = None
    if hasattr(files, 'file_id'):
        file_id = files.file_id
    if exists_post is None:
        created_post, created = InstagramPost.get_or_create(
            pk=post.pk,
            code=post.code,
            taken_at=post.taken_at,
            media_type=post.media_type,
            thumbnail_url=post.thumbnail_url,
            user=post.user.pk,
            caption_text=caption_text_to_db(post),
            telegram_file_id=file_id
        )
        if post.media_type == 8:
            dbm('Post is a album. Creating post resources')
            for i, resource in enumerate(post.resources):
                add_resource_to_instagram_post(resource, created_post, files, i)
            dbm(f'Created instagram post with pk:{post.pk} for {post.user.username}')
        return created_post
    else:
        dbm(f'Instagram post with pk:{post.pk} for {post.user.username} already exists')
        return exists_post


def create_or_get_instagram_user(instagram_user: InstagramUser, telegram_user: TelegramUser) -> InstagramUser:
    exists_instagram_user = InstagramUser.get_or_none(InstagramUser.pk == instagram_user.pk)
    if exists_instagram_user is None:
        s3 = AWS()
        profile_path = create_folder_by_username(instagram_user.username)

        profile_pic = requests.get(
            instagram_user.profile_pic_url_hd if instagram_user.profile_pic_url_hd is not None else instagram_user.profile_pic_url,
            allow_redirects=True)
        open(f'{profile_path}/{instagram_user.pk}_profile_pic.jpg', 'wb').write(profile_pic.content)
        pic_location = s3.upload_file(f'{profile_path}/{instagram_user.pk}_profile_pic.jpg',
                                      f'{instagram_user.pk}_profile_pic.jpg')

        created_user, created = InstagramUser.get_or_create(
            pk=instagram_user.pk,
            username=instagram_user.username,
            full_name=instagram_user.full_name,
            profile_pic_url=instagram_user.profile_pic_url,
            profile_pic_url_hd=instagram_user.profile_pic_url_hd,
            is_private=instagram_user.is_private,
            added_by=telegram_user.id,
            profile_pic_location=pic_location,
            enabled=True,
        )
        dbm(f'Instagram user {instagram_user.username} added by {telegram_user.username}')
        return created_user
    else:
        dbm(f'Instagram user {instagram_user.username} for {telegram_user.username} already exists')
        return exists_instagram_user


def add_resource_to_instagram_post(resource: InstagramPostResource,
                                   created_post: InstagramPost, files, current_index) -> InstagramPostResource:
    dbm('Adding resources to created instagram post')
    exists_resource = InstagramPostResource.get_or_none(InstagramPostResource.pk == resource.pk)
    file_id = None
    bigger_file = files[current_index]
    if hasattr(bigger_file, 'photo'):
        if bigger_file.photo is not None:
            file_id = bigger_file.photo[-1].file_id
    if hasattr(bigger_file, 'video'):
        if bigger_file.video is not None:
            file_id = bigger_file.video[-1].file_id
    if exists_resource is None:
        created_resource, created = InstagramPostResource.get_or_create(
            pk=resource.pk,
            video_url=resource.video_url,
            thumbnail_url=resource.thumbnail_url,
            media_type=resource.media_type,
            post=created_post.id,
            telegram_file_id=file_id
        )
        dbm(f'Created instagram resource with pk:{resource.pk} for {created_post.id}')
        return created_resource
    else:
        dbm(f'Instagram resource with pk:{resource.pk} for {created_post.id} already exists')
        return exists_resource


def add_instagram_story_to_instagram_user(story: InstagramStory, telegram_user_id, files) -> InstagramStory:
    telegram_user = get_current_telegram_user(telegram_user_id)
    create_or_get_instagram_user(story.user, telegram_user)
    exists_story = InstagramStory.get_or_none(InstagramStory.pk == story.pk)
    file_id = None
    if hasattr(files, 'file_id'):
        file_id = files.file_id
    if exists_story is None:
        created_story, created = InstagramStory.get_or_create(
            pk=story.pk,
            code=story.code,
            taken_at=story.taken_at,
            media_type=story.media_type,
            thumbnail_url=story.thumbnail_url,
            video_url=story.video_url,
            video_duration=story.video_duration,
            user=story.user.pk,
            caption_text=caption_text_to_db(story),
            telegram_file_id=file_id
        )
        dbm(f'Created instagram story with pk:{story.pk} for {story.user.username}')
        return created_story
    else:
        dbm(f'Instagram story with pk:{story.pk} for {story.user.username} already exists')
        return exists_story


def add_instagram_highlight_to_instagram_user(highlight, telegram_user_id, files) -> InstagramHighlight:
    telegram_user = get_current_telegram_user(telegram_user_id)
    create_or_get_instagram_user(highlight.user, telegram_user)
    exists_highlight = InstagramHighlight.get_or_none(InstagramHighlight.pk == highlight.pk)
    file_id = None
    if hasattr(files, 'file_id'):
        file_id = files.file_id
    if exists_highlight is None:
        created_highlight, created = InstagramHighlight.get_or_create(
            pk=highlight.pk,
            code=highlight.code,
            taken_at=highlight.taken_at,
            media_type=highlight.media_type,
            thumbnail_url=highlight.thumbnail_url,
            video_url=highlight.video_url,
            video_duration=highlight.video_duration,
            user=highlight.user.pk,
            caption_text=caption_text_to_db(highlight),
            telegram_file_id=file_id
        )
        dbm(f'Created instagram highlight with pk:{highlight.pk} for {highlight.user.username}')
        return created_highlight
    else:
        dbm(f'Instagram highlight with pk:{highlight.pk} for {highlight.user.username} already exists')
        return exists_highlight


def clean_all_instagram_account_works():
    dbm('Clean all instagram accounts downloading works')
    InstagramAccount.update({InstagramAccount.downloading_now: False}).execute()
