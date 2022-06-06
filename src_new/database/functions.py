from database.misc import get_db
from database.models import TUser, TUserStatus, IUser, IAccount, IPost, IPostResource, IStory, TUserIUsers


def initialize_db():
    db = get_db()
    db.connect()
    db.create_tables(
        [TUser, TUserStatus, IUser,
         IAccount, IPost, IPostResource,
         IStory, TUserIUsers])
    db.close()
    initialize_user_statuses()


def initialize_user_statuses():
    TUserStatus.get_or_create(name='Usual')
    TUserStatus.get_or_create(name='Normal')
    TUserStatus.get_or_create(name='Banned')
    TUserStatus.get_or_create(name='VIP')
    TUserStatus.get_or_create(name='Admin')
