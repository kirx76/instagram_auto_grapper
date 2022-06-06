import os
from typing import Union

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.types import User

from database.get import get_tuser_iaccount
from database.models import IAccount, TUser
from database.set import save_iaccount_dump_data

load_dotenv()


class CL:
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
                print(iuser_data)
                return True, iuser_data
            except Exception as e:
                print(e)
                return False, 'Error'


def check_iuser_validity(tuser: TUser, iuser_username: str) -> tuple[bool, str]:
    iaccount = get_tuser_iaccount(tuser)
    cl = CL(iaccount)
    cl.login()
    is_valid, iuser_data = cl.get_iuser_data(iuser_username)
    print('is_valid', is_valid)
    return is_valid, iuser_data


def check_iaccount_validity(username: str, password: str) -> Union[bool, tuple[bool, Union[Exception, str]]]:
    cl = Client()
    try:
        cl.login(username, password, True)
        cl.get_timeline_feed()
        return True, 'Success'
    except Exception as e:
        print(e)
        return False, e


def init_iaccount(iaccount: IAccount):
    cl = Client()

    dump_data = iaccount.dump_data
    if dump_data is None:
        cl.login(iaccount.username, iaccount.password, True)
    else:
        with open(f'{os.environ.get("IG_DUMP_FOLDER_PATH")}{iaccount.username}.json', 'w') as f:
            f.write(dump_data)
        cl.load_settings(f'{os.environ.get("IG_DUMP_FOLDER_PATH")}{iaccount.username}.json')
        cl.login(iaccount.username, iaccount.password, False)
    try:
        cl.get_timeline_feed()
        cl.dump_settings(f'{os.environ.get("IG_DUMP_FOLDER_PATH")}{iaccount.username}.json')
        save_iaccount_dump_data(f'{os.environ.get("IG_DUMP_FOLDER_PATH")}{iaccount.username}.json')
        return True
    except Exception as e:
        print(e)
        return False
