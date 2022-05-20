import time

from telebot.types import InputMediaPhoto

from utils.misc import collect_caption_to_send, err, cleanup_downloaded_file_by_filepath


def download_and_send_photo(bot, media, message, username, cl):
    downloaded_photo_path = cl.photo_download(media.pk, folder=f'./downloads/{username}')
    time.sleep(2)
    bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_photo_path, 'rb'),
                   caption=collect_caption_to_send(media, username))
    cleanup_downloaded_file_by_filepath(downloaded_photo_path)
    return True


def download_and_send_highlight(bot, highlight, message, username, cl):
    try:
        downloaded_highlight_path = cl.story_download(highlight.pk, folder=f'./downloads/{username}')
        time.sleep(2)
        if highlight.media_type in [0, 1]:
            bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_highlight_path, 'rb'),
                           caption=collect_caption_to_send(highlight, username))
            cleanup_downloaded_file_by_filepath(downloaded_highlight_path)
            return True
        elif highlight.media_type == 2:
            bot.send_video(chat_id=message.chat.id, video=open(downloaded_highlight_path, 'rb'),
                           supports_streaming=True,
                           caption=collect_caption_to_send(highlight, username))
            cleanup_downloaded_file_by_filepath(downloaded_highlight_path)
            return True
        return False
    except Exception as e:
        err(f'Тут снова ошибка ебаная на хайлайтах при загрузке, чекай: {e}')
        return False


def download_and_send_story(bot, story, message, username, cl):
    try:
        downloaded_story_path = cl.story_download(story.pk, folder=f'./downloads/{username}')
        time.sleep(2)
        if story.media_type in [0, 1]:
            bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_story_path, 'rb'),
                           caption=collect_caption_to_send(story, username))
            cleanup_downloaded_file_by_filepath(downloaded_story_path)
            return True
        elif story.media_type == 2:
            bot.send_video(chat_id=message.chat.id, video=open(downloaded_story_path, 'rb'), supports_streaming=True,
                           caption=collect_caption_to_send(story, username))
            cleanup_downloaded_file_by_filepath(downloaded_story_path)
            return True
        return False
    except Exception as e:
        err(f'Тут снова ошибка ебаная на сторисах при загрузке, чекай: {e}')
        return False


def download_and_send_video(bot, video, message, username, cl):
    downloaded_video_path = cl.video_download(video.pk, folder=f'./downloads/{username}')
    time.sleep(2)
    bot.send_video(chat_id=message.chat.id, video=open(downloaded_video_path, 'rb'), supports_streaming=True,
                   caption=collect_caption_to_send(video, username))
    cleanup_downloaded_file_by_filepath(downloaded_video_path)
    return True


def download_and_send_album(bot, album, message, username, cl):
    downloaded_photo_paths = cl.album_download(album.pk, folder=f'./downloads/{username}')
    data = []
    # TODO IF ALBUM HAVE A VIDEO -> SENDS THUMBNAIL OF VIDEO NOT VIDEO
    for i, source in enumerate(downloaded_photo_paths):
        if i == 0:
            data.append(InputMediaPhoto(open(source, 'rb'), caption=collect_caption_to_send(album, username)))
        else:
            data.append(InputMediaPhoto(open(source, 'rb')))
    time.sleep(2)
    bot.send_media_group(message.chat.id, data)
    for source in downloaded_photo_paths:
        cleanup_downloaded_file_by_filepath(source)
    return True
