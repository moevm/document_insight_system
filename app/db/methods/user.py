import pymongo

from app.db.db_main import get_users_collection
from app.db.types.User import User

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
    user = users_collection.find_one({'username': username, 'password_hash': password_hash})
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


def set_user_role(username, is_admin):
    result = users_collection.update_one({'username': username}, {'$set': {'is_admin': is_admin}})
    return result.matched_count == 1


def get_user_cursor(filter=None, limit=10, offset=0, sort=None, order=None):
    filter = filter or {}
    sort = {'all_formats': 'formats', 'all_criteria': 'criteria', 'role': 'is_admin'}.get(sort, sort)
    count = users_collection.count_documents(filter)
    if sort == 'check_counts':
        pipeline = [
            {'$match': filter},
            {'$addFields': {'_check_count': {'$size': {'$ifNull': ['$files', []]}}}},
            {'$sort': {'_check_count': 1 if order == 'asc' else -1, 'username': 1}},
            {'$skip': offset},
        ]
        if limit:
            pipeline.append({'$limit': limit})
        return users_collection.aggregate(pipeline), count
    rows = users_collection.find(filter)
    if sort and order in ('asc', 'desc'):
        rows = rows.sort([(sort, pymongo.ASCENDING if order == 'asc' else pymongo.DESCENDING), ('_id', 1)])
    return rows.skip(offset).limit(limit), count
