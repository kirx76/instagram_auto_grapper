from database.models import TUser, IAccount, IUser


def get_iaccounts_list(tuser: TUser) -> list[IAccount]:
    return IAccount.select().where(IAccount.owner == tuser.id).execute()


def get_iaccount_by_username(iaccount_username: str) -> IAccount:
    return IAccount.get(IAccount.username == iaccount_username)


def get_tuser(tuser_user_id) -> TUser:
    return TUser.get(TUser.user_id == tuser_user_id)


def get_iusers_list(tuser: TUser) -> list[IUser]:
    return tuser.i_users.execute()


def get_tuser_iaccount(tuser: TUser) -> IAccount:
    return tuser.i_accounts.first()
