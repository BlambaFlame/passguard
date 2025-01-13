from peewee import *
import datetime

from passwords import encrypt_password, decrypt_password

db = SqliteDatabase('db/database.sqlite3')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    tg_uid = CharField(primary_key=True)
    password = CharField()


class Account(BaseModel):
    user = ForeignKeyField(User, backref='accounts')
    account_source = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    password = CharField()


db.connect()
db.create_tables([User, Account])


def save_user(tg_uid: str, password: str) -> None:

    user = User(
        tg_uid=tg_uid,
        password=encrypt_password(password)
    )
    user.save()


def delete_user(tg_uid: str) -> None:

    query = Account.delete().where(Account.user == tg_uid)
    query.execute()
    user = User.get(tg_uid=tg_uid)
    user.delete_instance()


def save_account_pass(tg_uid: str, account_source: str, password: str) -> None:
    account = Account(
        user=tg_uid,
        account_source=account_source.lower(),
        password=encrypt_password(password)
    )
    account.save()


def delete_account_pass(tg_uid: str, account_source: str) -> None:
    account = Account(
        user=tg_uid,
        account_source=account_source.lower(),
    )
    account.delete_instance()


def update_account_pass(tg_uid: str, account_source: str, password: str) -> None:
    account = Account(
        user=tg_uid,
        account_source=account_source.lower(),
    )
    account.password = encrypt_password(password)
    account.save()


def get_account_pass(tg_uid: str, account_source: str) -> str:
    account = Account.get(user=tg_uid, account_source=account_source)
    return decrypt_password(account.password)


def get_user_accounts_all(tg_uid: str) -> list:
    query = Account.select()
    return [account.account_source for account in query]


# Пример использования
if __name__ == "__main__":
    users = (
        ('testuser1', 'testpass1'),
        ('testuser2', 'testpass2'),
        ('testuser3', 'testpass3'),
    )
    accounts = (
        ('github', 'githubpass'),
        ('yandex', 'yandexpass'),
        ('google', 'googlepass'),
        ('steam', 'steampass'),
    )

    for user in users:
        save_user(*user)
        print(user[0])
        for account in accounts:
            save_account_pass(user[0], account[0], account[1])

        for x in get_user_accounts_all(user[0]):
            print(x)
            print(get_account_pass(user[0], x))


