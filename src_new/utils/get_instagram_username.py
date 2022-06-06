import re

from urllib.parse import urlparse


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError as e:
        print(e)
        return False


def get_instagram_username(url):
    if is_url(url):
        return re.search('(?:(?:http|https):\/\/)?(?:www\.)?(?:instagram\.com|instagr\.am)\/([A-Za-z0-9-_\.]+)', url)[1]
    else:
        return url
