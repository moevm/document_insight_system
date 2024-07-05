from gridfs import GridFSBucket, NoFile
from datetime import datetime

import pymongo

from app.db.db_methods import get_checks_collection, get_users_collection, get_files_info_collection
from app.db.methods.client import get_client, get_db, get_fs
from app.db.types.Check import Check


# client = get_client()
db = get_db()
fs = get_fs()

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


# Returns presentations parsed_file with given id or None

def get_checks_pdf(checks_id):
    checks = checks_collection.find_one({'_id': checks_id})
    pdf_id = checks.get('conv_pdf_fs_id')
    try:
        return fs.open_download_stream(pdf_id)
    except NoFile:
        return None


def delete_check(presentation, checks_id):
    if checks_id in presentation.checks:
        upd_presentation = files_info_collection.update_one(
            {'_id': presentation._id}, {"$pull": {'checks': checks_id}})
        checks = Check(
            checks_collection.find_one_and_delete({'_id': checks_id}))
        fs.delete(checks_id)
        return presentation, checks
    else:
        return presentation, get_check(checks_id)


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
    local_filter = filter
    user = local_filter.get('user')
    username_filter = {'username': user} if user else {}
    all_users = [user['username'] for user in users_collection.find(username_filter, {'username': 1})]
    latest_checks = []
    for user in all_users:
        local_filter['user'] = user
        check, count = get_checks_cursor(local_filter, limit=1, sort='_id', order='desc')
        if count:
            latest_checks.append(check[0])
    return latest_checks, len(latest_checks)


def get_latest_user_check_by_moodle(moodle_id):
    return list(db.checks.find(
        {'lms_user_id': moodle_id}
    ).sort('_id', -1).limit(1))


def get_latest_check_cursor(filter, *args, **kwargs):
    return get_latest_users_check(filter)


def get_all_checks():
    return checks_collection.find()


def get_checks(filter={}, latest=None, limit=10, offset=0, sort=None, order=None):
    if latest:
        return get_latest_check_cursor(filter, limit, offset, sort, order)
    else:
        return get_checks_cursor(filter, limit, offset, sort, order)


def get_checks_cursor(filter={}, limit=10, offset=0, sort=None, order=None):
    sort = 'lms_passback_time' if sort == 'moodle-date' else sort

    count = checks_collection.count_documents(filter)
    rows = checks_collection.find(filter)

    if sort and order in ("asc, desc"):
        rows = rows.sort(sort, pymongo.ASCENDING if order ==
                                                    "asc" else pymongo.DESCENDING)

    rows = rows.skip(offset) if offset else rows
    rows = rows.limit(limit) if limit else rows

    return rows, count


# get logs cursor with specified parameters



def get_user_checks(login):
    return checks_collection.find({'user': login})


def get_check_stats(oid):
    return checks_collection.find_one({'_id': oid})








