from typing import Union

from instagrapi.types import User
from telebot import TeleBot
from telebot.types import Message

from database.get import check_tuser_in_iuser
from database.models import IAccount, IUser, TUser
from utils.get_bigger_file import get_bigger_photo
from utils.models.IAccountModel import IAccountModel


class IUserModel:
    def __init__(self, iuser_username: str, iaccount: IAccount):
        self.iuser: Union[IUser, None] = None
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

    def get_user_from_db(self):
        self.iuser = IUser.get(IUser.username == self.iuser_username)
        return self.iuser

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
            exists_iuser = IUser.get_or_none(IUser.pk == self.user_data.pk)
            is_tuser_exists_in_iuser = check_tuser_in_iuser(exists_iuser, owner)
            if is_tuser_exists_in_iuser:
                pass
            else:
                exists_iuser.available_for.add(owner)

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

    def get_posts_list(self):
        try:
            self.log()
            user_id = int(self.iaccount.cl.user_id_from_username(self.iuser.username))
            return self.iaccount.cl.user_medias(user_id)
        except Exception as e:
            print(e)

    def log(self):
        if not self.iaccount.logined:
            self.iaccount.login()
        if not self.iuser:
            self.get_user_from_db()

    def get_new_posts(self):
        self.log()
        posts = self.get_posts_list()
        posts_in_db = self.iuser.posts.execute()
        iu_posts_pks = [int(y.pk) for y in posts_in_db]
        posts_pks = [int(post.pk) for post in posts]
        filtered_list_of_posts_pks = list(set(posts_pks) - set(iu_posts_pks))
        done_posts = []
        for pk in filtered_list_of_posts_pks:
            done_posts += ([x for x in posts if int(x.pk) == pk])
        return done_posts

    def get_posts(self, bot: TeleBot, message: Message):
        self.log()
        new_posts = self.get_new_posts()
        print(len(new_posts), new_posts)
