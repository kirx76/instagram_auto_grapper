from database.models import TUser, IAccount, IUser, TUserIUsers


def get_iaccounts_list(tuser: TUser) -> list[IAccount]:
    return IAccount.select().where(IAccount.owner == tuser.id).execute()


def get_iaccount_by_username(iaccount_username: str) -> IAccount:
    return IAccount.get(IAccount.username == iaccount_username)


def get_iuser_by_username(iuser_username: str) -> IUser:
    return IUser.get(IUser.username == iuser_username)


def get_tuser(tuser_user_id) -> TUser:
    return TUser.get(TUser.user_id == tuser_user_id)


def get_iusers_list(tuser: TUser) -> list[IUser]:
    return tuser.i_users.execute()


def get_tuser_iaccount(tuser: TUser) -> IAccount:
    return tuser.i_accounts.first()


def check_tuser_in_iuser(iuser: IUser, tuser: TUser):
    iuser_available_for = iuser.available_for.where(TUserIUsers.tuser_id == tuser.id).first()
    if iuser_available_for is None:
        return False
    else:
        return True
