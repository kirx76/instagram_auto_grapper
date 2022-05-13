import time

from telebot.types import InputMediaPhoto

from misc import collect_caption_to_send, err


def download_and_send_photo(bot, media, message, username, cl):
    downloaded_photo_path = cl.photo_download(media.pk, folder=f'./downloads/{username}')
    time.sleep(2)
    bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_photo_path, 'rb'),
                   caption=collect_caption_to_send(media, username))
    return True


def download_and_send_highlight(bot, highlight, message, username, cl):
    try:
        downloaded_highlight_path = cl.story_download(highlight.pk, folder=f'./downloads/{username}')
        if highlight.media_type == 0:
            time.sleep(2)
            bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_highlight_path, 'rb'),
                           caption=collect_caption_to_send(highlight, username))
            return True
        if highlight.media_type == 1:
            time.sleep(2)
            bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_highlight_path, 'rb'),
                           caption=collect_caption_to_send(highlight, username))
            return True
        if highlight.media_type == 2:
            time.sleep(2)
            bot.send_video(chat_id=message.chat.id, video=open(downloaded_highlight_path, 'rb'),
                           supports_streaming=True,
                           caption=collect_caption_to_send(highlight, username))
            return True
        return False
    except Exception as e:
        err(f'Тут снова ошибка ебаная на хайлайтах при загрузке, чекай: {e}')
        return False


def download_and_send_story(bot, story, message, username, cl):
    try:
        downloaded_story_path = cl.story_download(story.pk, folder=f'./downloads/{username}')
        if story.media_type == 0:
            time.sleep(2)
            bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_story_path, 'rb'),
                           caption=collect_caption_to_send(story, username))
            return True
        if story.media_type == 1:
            time.sleep(2)
            bot.send_photo(chat_id=message.chat.id, photo=open(downloaded_story_path, 'rb'),
                           caption=collect_caption_to_send(story, username))
            return True
        if story.media_type == 2:
            time.sleep(2)
            bot.send_video(chat_id=message.chat.id, video=open(downloaded_story_path, 'rb'), supports_streaming=True,
                           caption=collect_caption_to_send(story, username))
            return True
        return False
    except Exception as e:
        err(f'Тут снова ошибка ебаная на хайлайтах при загрузке, чекай: {e}')
        return False


def download_and_send_video(bot, video, message, username, cl):
    downloaded_video_path = cl.video_download(video.pk, folder=f'./downloads/{username}')
    time.sleep(2)
    bot.send_video(chat_id=message.chat.id, video=open(downloaded_video_path, 'rb'), supports_streaming=True,
                   caption=collect_caption_to_send(video, username))
    return True


def download_and_send_album(bot, album, message, username, cl):
    downloaded_photo_paths = cl.album_download(album.pk, folder=f'./downloads/{username}')
    data = []
    for i, source in enumerate(downloaded_photo_paths):
        if i == 0:
            data.append(InputMediaPhoto(open(source, 'rb'), caption=collect_caption_to_send(album, username)))
        else:
            data.append(InputMediaPhoto(open(source, 'rb')))
    time.sleep(2)
    bot.send_media_group(message.chat.id, data)
    return True
