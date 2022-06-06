from operator import attrgetter
from typing import Union

from telebot.types import PhotoSize


def get_bigger_photo(photos: Union[PhotoSize, list[PhotoSize]]):
    if isinstance(photos, list):
        return max(photos, key=attrgetter('file_size'))
    else:
        return photos
