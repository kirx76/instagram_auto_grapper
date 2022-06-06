import os

from instagrapi.types import User
from telebot.types import Message

from database.models import TUser, IAccount, IUser
from utils.models.IUserModel import IUserModel


def create_or_get_tuser(message: Message) -> TUser:
    user, created = TUser.get_or_create(username=message.from_user.username, user_id=message.from_user.id)
    print('create_or_get_tuser', created)
    return user


def create_or_get_iaccount(username: str, password: str, tuser: TUser) -> (IAccount, bool):
    iaccount, created = IAccount.get_or_create(username=username, password=password, owner=tuser.id)
    print('create_or_get_iaccount', created)
    return iaccount, created


def save_iaccount_dump_data(path: str, iaccount: IAccount):
    if os.path.exists(path):
        text_file = open(path, "r")
        data = text_file.read()
        text_file.close()
        IAccount.update({IAccount.dump_data: data}).where(
            IAccount.username == iaccount.username).execute()
        os.remove(path)

