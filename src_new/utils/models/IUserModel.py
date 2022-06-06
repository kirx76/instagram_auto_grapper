from typing import Union

from instagrapi.types import User
from telebot import TeleBot
from telebot.types import Message

from bot.markups.user_markup import user_iuser_accept
from database.models import IAccount, IUser, TUser
from utils.get_bigger_file import get_bigger_photo
from utils.models.IAccountModel import IAccountModel


class IUserModel:
    def __init__(self, iuser_username: str, iaccount: IAccount):
        self.iuser_username = iuser_username
        self.user_data: Union[User, None] = None
        self.biggest_photo_id: Union[str, None] = None
        self.iaccount = IAccountModel(iaccount)

    def get_name(self):
        return self.user_data.username

    def get_pk(self):
        return self.user_data.pk

    def check_if_exists_db(self):
        exists = IUser.get_or_none(IUser.pk == self.user_data.pk)
        if exists is not None:
            return True
        else:
            return False

    def save_to_db(self, owner: TUser = None):
        exists = self.check_if_exists_db()
        if not exists:
            created_user, created = IUser.get_or_create(
                pk=self.user_data.pk,
                username=self.user_data.username,
                full_name=self.user_data.full_name,
                profile_pic_url=self.user_data.profile_pic_url,
                profile_pic_url_hd=self.user_data.profile_pic_url_hd,
                is_private=self.user_data.is_private,
                added_by=owner.id,
                enabled=True,
                telegram_file_id=self.biggest_photo_id
            )
            created_user.available_for.add(owner)
            return created_user
        else:


    def get_user_data(self):
        try:
            self.iaccount.login()
            is_valid = self.iaccount.check()
            if is_valid:
                is_iuser_valid, iuser_data = self.iaccount.get_iuser_data(self.iuser_username)
                if is_iuser_valid:
                    self.user_data = iuser_data
                    return self.user_data
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def send_profile_pic_to_user(self, bot: TeleBot, message: Message):
        msg = bot.send_photo(chat_id=message.chat.id, photo=self.user_data.profile_pic_url_hd,
                             caption=f'Founded')
        biggest_photo = get_bigger_photo(msg.photo)
        self.biggest_photo_id = biggest_photo.file_id
        return msg
