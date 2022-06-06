import os
from typing import Union

from dotenv import load_dotenv
from instagrapi import Client

from database.get import get_tuser_iaccount
from database.models import IAccount, TUser
from database.set import save_iaccount_dump_data
from utils.models.IAccountModel import IAccountModel

load_dotenv()


# def check_iuser_validity(tuser: TUser, iuser_username: str) -> tuple[bool, str]:
#     iaccount = get_tuser_iaccount(tuser)
#     cl = IAccountModel(iaccount)
#     cl.login()
#     is_valid, iuser_data = cl.get_iuser_data(iuser_username)
#     print('is_valid', is_valid)
#     return is_valid, iuser_data


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
