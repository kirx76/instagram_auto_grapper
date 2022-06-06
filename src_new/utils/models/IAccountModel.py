from typing import Union

from instagrapi import Client
from instagrapi.types import User

from database.models import IAccount


class IAccountModel:
    def __init__(self, iaccount: IAccount):
        self.cl = Client()
        self.account_data = iaccount
        self.logined = False

    def login(self):
        self.cl.login(self.account_data.username, self.account_data.password, False)
        self.logined = True

    def relogin(self):
        self.cl.login(self.account_data.username, self.account_data.password, True)
        self.logined = True

    def check(self):
        if self.logined:
            try:
                self.cl.get_timeline_feed()
                return True
            except Exception as e:
                print(e)
                return False

    def get_iuser_data(self, iuser_username: str) -> Union[tuple[bool, User], tuple[bool, str]]:
        if self.logined:
            try:
                iuser_data = self.cl.user_info_by_username(iuser_username)
                return True, iuser_data
            except Exception as e:
                print(e)
                return False, 'Error'
