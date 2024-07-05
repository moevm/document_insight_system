import pymongo

from app.db.db_methods import get_users_collection
from app.db.methods.client import get_db
from app.db.types.User import User

from app.db.methods.file import delete_presentation


# client = get_client()
db = get_db()
# fs = get_fs()

users_collection = get_users_collection()


def add_user(username, password_hash='', is_LTI=False):
    user = User()
    user.username = username
    user.is_LTI = is_LTI
    if not is_LTI:
        user.password_hash = password_hash
    if users_collection.find_one({'username': username}) is not None:
        return None
    else:
        users_collection.insert_one(user.pack())
        return user


def validate_user(username, password_hash):
    user = users_collection.find_one(
        {'username': username, 'password_hash': password_hash})
    if user is not None:
        return User(user)
    else:
        return None


def get_user(username):
    user = users_collection.find_one({'username': username})
    if user is not None:
        return User(user)
    else:
        return None


def get_all_users():
    return users_collection.find()


def delete_user(username):
    user = get_user(username)
    for presentation_id in user.presentations:
        user, presentation = delete_presentation(user, presentation_id)
    user = User(users_collection.find_one_and_delete({'username': username}))
    return user


def get_user_cursor(filter={}, limit=10, offset=0, sort=None, order=None):
    sort = 'username' if sort == 'username' else sort

    count = users_collection.count_documents(filter)
    rows = users_collection.find(filter)

    if sort and order in ("asc, desc"):
        rows = rows.sort(sort, pymongo.ASCENDING if order ==
                                                    "asc" else pymongo.DESCENDING)

    rows = rows.skip(offset) if offset else rows
    rows = rows.limit(limit) if limit else rows

    return rows, count
#
# def edit_user(user):
#     if users_collection.find_one_and_replace({'username': user.username}, user.pack()) is not None:
#         return True
#     else:
#         return False