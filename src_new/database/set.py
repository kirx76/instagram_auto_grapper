import os

from instagrapi.types import User
from telebot.types import Message

from database.models import TUser, IAccount, IUser


def create_or_get_tuser(message: Message) -> TUser:
    user, created = TUser.get_or_create(username=message.from_user.username, user_id=message.from_user.id)
    print('create_or_get_tuser', created)
    return user


def create_or_get_iaccount(username: str, password: str, tuser: TUser) -> (IAccount, bool):
    iaccount, created = IAccount.get_or_create(username=username, password=password, owner=tuser.id)
    print('create_or_get_iaccount', created)
    return iaccount, created


def create_or_get_iuser(iuser: User, tuser: TUser):
    iuser, created = IUser.get_or_create(
        pk=iuser.pk,
        username=iuser.username,
        full_name=iuser.full_name,
        profile_pic_url=iuser.profile_pic_url,
        profile_pic_url_hd=iuser.profile_pic_url_hd,
        is_private=iuser.is_private,
        added_by=tuser.id,
        profile_pic_location=telegram_file_id,
        enabled=True,
    )


def save_iaccount_dump_data(path: str, iaccount: IAccount):
    if os.path.exists(path):
        text_file = open(path, "r")
        data = text_file.read()
        text_file.close()
        IAccount.update({IAccount.dump_data: data}).where(
            IAccount.username == iaccount.username).execute()
        os.remove(path)

