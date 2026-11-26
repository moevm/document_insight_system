from datetime import datetime

import pymongo

from app.db.db_main import get_checks_collection, get_files_info_collection, get_users_collection
from app.db.methods.client import get_db
from app.db.types.Check import Check

db = get_db()

checks_collection = get_checks_collection()

users_collection = get_users_collection()
files_info_collection = get_files_info_collection()


def add_check(file_id, check):
    checks_id = checks_collection.insert_one(check.pack()).inserted_id
    files_info_collection.update_one({'_id': file_id}, {"$push": {'checks': checks_id}})
    return checks_id


def update_check(check):
    return bool(checks_collection.find_one_and_replace({'_id': check._id}, check.pack()))


def get_check(checks_id):
    checks = checks_collection.find_one({'_id': checks_id})
    if checks is not None:
        return Check(checks)
    else:
        return None


def get_unpassed_checks():
    return checks_collection.find({'is_passbacked': False})


def set_passbacked_flag(checks_id, flag):
    upd_check = {"$set": {}}
    upd_check['$set']['is_passbacked'] = flag

    if flag is None:
        # flag = None - if user without passback
        upd_check['$set']['lms_passback_time'] = None
    elif flag:
        upd_check['$set']['lms_passback_time'] = datetime.now()

    check = checks_collection.update_one({'_id': checks_id}, upd_check)
    return check if check else None


def get_latest_users_check(filter=None):
    return get_latest_check_cursor(filter or {}, limit=0)


def get_latest_user_check_by_moodle(moodle_id):
    return list(db.checks.find({'lms_user_id': moodle_id}).sort('_id', -1).limit(1))


def get_latest_check_cursor(filter=None, limit=10, offset=0, sort=None, order=None):
    sort = {'upload-date': '_id', 'moodle-date': 'lms_passback_time'}.get(sort, sort) or '_id'
    rows = [{'$sort': {sort: 1 if order == 'asc' else -1, **({'_id': -1} if sort != '_id' else {})}}]
    if offset:
        rows.append({'$skip': offset})
    if limit:
        rows.append({'$limit': limit})
    pipeline = [
        {'$match': filter or {}},
        {'$sort': {'_id': -1}},
        {'$group': {'_id': '$user', 'check': {'$first': '$$ROOT'}}},
        {'$replaceRoot': {'newRoot': '$check'}},
        {'$facet': {'rows': rows, 'count': [{'$count': 'total'}]}},
    ]
    if not limit and not offset:
        all_rows = list(checks_collection.aggregate(pipeline[:-1] + rows))
        return all_rows, len(all_rows)
    result = next(iter(checks_collection.aggregate(pipeline)), {'rows': [], 'count': []})
    return result['rows'], result['count'][0]['total'] if result['count'] else 0


def get_checks(filter=None, latest=None, limit=10, offset=0, sort=None, order=None):
    filter = filter or {}
    if latest:
        return get_latest_check_cursor(filter, limit, offset, sort, order)
    else:
        return get_checks_cursor(filter, limit, offset, sort, order)


def get_checks_cursor(filter=None, limit=10, offset=0, sort=None, order=None):
    filter = filter or {}
    sort = 'lms_passback_time' if sort == 'moodle-date' else sort

    count = checks_collection.count_documents(filter)
    rows = checks_collection.find(filter)

    if sort and order in ('asc', 'desc'):
        rows = rows.sort(
            [(sort, pymongo.ASCENDING if order == 'asc' else pymongo.DESCENDING)]
            + ([('_id', -1)] if sort != '_id' else [])
        )

    rows = rows.skip(offset) if offset else rows
    rows = rows.limit(limit) if limit else rows

    return rows, count
