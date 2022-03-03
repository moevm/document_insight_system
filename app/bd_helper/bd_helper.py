from os.path import basename
from gridfs import GridFSBucket, NoFile
from pymongo import MongoClient
from bson import ObjectId
import pymongo

from app.bd_helper.bd_types import User, Presentation, Checks, Consumers, CriteriaPack, Logs
from app.utils.pdf_converter import convert_to_pdf

from datetime import datetime, timezone

client = MongoClient("mongodb://mongodb:27017")
db = client['pres-parser-db']
fs = GridFSBucket(db)

users_collection = db['users']
presentations_collection = db['presentations']
checks_collection = db['checks']
consumers_collection = db['consumers']
criteria_pack_collection = db['criteria_pack']
logs_collection = db.create_collection(
    'logs', capped=True, size=5242880) if not db['logs'] else db['logs']


def get_client():
    return client


# Returns user if user was created and None if already exists
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


# Returns user if there was user with given credentials and None if not
def validate_user(username, password_hash):
    user = users_collection.find_one(
        {'username': username, 'password_hash': password_hash})
    if user is not None:
        return User(user)
    else:
        return None


# Returns user with given username or None
def get_user(username):
    user = users_collection.find_one({'username': username})
    if user is not None:
        return User(user)
    else:
        return None


# Returns True if user was found and updated and false if not (username can not be changed!)
def edit_user(user):
    if users_collection.find_one_and_replace({'username': user.username}, user.pack()) is not None:
        return True
    else:
        return False


# Deletes user with given username, deleting also all his presentations and their checks, returns user
def delete_user(username):
    user = get_user(username)
    for presentation_id in user.presentations:
        user, presentation = delete_presentation(user, presentation_id)
    user = User(users_collection.find_one_and_delete({'username': username}))
    return user


# Adds presentation with given name to given user presentations, updates user, returns user and presentation id
def add_presentation(user, presentation_name):
    presentation = Presentation()
    presentation.name = presentation_name
    presentation_id = presentations_collection.insert_one(
        presentation.pack()).inserted_id
    user.presentations.append(presentation_id)
    edit_user(user)
    return user, presentation_id


# Returns presentation with given id or None
def get_presentation(presentation_id):
    presentation = presentations_collection.find_one({'_id': presentation_id})
    if presentation is not None:
        return Presentation(presentation)
    else:
        return None


# Returns presentation of given user with given id or None
def find_presentation(user, presentation_name):
    presentations = []
    for presentation_id in user.presentations:
        presentations.append(get_presentation(presentation_id))
    presentation = next(
        (x for x in presentations if x.name == presentation_name), None)
    if presentation is not None:
        return presentation
    else:
        return None


# Deletes presentation with given id, deleting also its checks, returns presentation
def delete_presentation(user, presentation_id):
    if presentation_id in user.presentations:
        user.presentations.remove(presentation_id)
        edit_user(user)
        presentation = get_presentation(presentation_id)
        for check_id in presentation.checks:
            presentation, check = delete_check(presentation, check_id)
        presentation = Presentation(
            presentations_collection.find_one_and_delete({'_id': presentation_id}))
        return user, presentation
    else:
        return user, get_presentation(presentation_id)


# Creates checks from given user check-list
def create_check(user):
    return Checks({'enabled_checks': user.criteria})


# Adds checks to given presentation, updates presentation, returns presentation and checks id
def add_check(presentation, checks, presentation_file):
    checks_id = checks_collection.insert_one(checks.pack()).inserted_id
    upd_presentation = presentations_collection.update_one(
        {'_id': presentation._id}, {"$push": {'checks': checks_id}})

    grid_in = fs.open_upload_stream_with_id(
        checks_id, basename(presentation_file))
    grid_in.write(open(presentation_file, 'rb'))
    grid_in.close()

    return presentation, checks_id


def add_api_check(checks, presentation_file):
    checks_id = checks_collection.insert_one(checks.pack()).inserted_id

    grid_in = fs.open_upload_stream_with_id(
        checks_id, basename(presentation_file))
    grid_in.write(open(presentation_file, 'rb'))
    grid_in.close()

    return checks_id


def write_pdf(file):
    extension = file.filename.rsplit('.', 1)[-1].lower()
    converted = 'pdf'.join(file.filename.rsplit(extension, 1))
    convert2pdf = convert_to_pdf(file)

    id = ObjectId()
    grid_in = fs.open_upload_stream_with_id(id, converted)
    grid_in.write(convert2pdf)
    grid_in.close()
    return id


# Returns checks with given id or None
def get_check(checks_id):
    checks = checks_collection.find_one({'_id': checks_id})
    if checks is not None:
        return Checks(checks)
    else:
        return None


# Returns presentation file with given id or None
def get_presentation_check(checks_id):
    try:
        return fs.open_download_stream(checks_id)
    except NoFile:
        return None


def get_checks_pdf(checks_id):
    checks = checks_collection.find_one({'_id': checks_id})
    pdf_id = checks.get('conv_pdf_fs_id')
    try:
        return fs.open_download_stream(pdf_id)
    except NoFile:
        return None


def find_pdf_by_file_id(file_id):
    try:
        return fs.open_download_stream(file_id)
    except NoFile:
        return None


# Deletes checks with given id, returns presentation
def delete_check(presentation, checks_id):
    if checks_id in presentation.checks:
        upd_presentation = presentations_collection.update_one(
            {'_id': presentation._id}, {"$pull": {'checks': checks_id}})
        checks = Checks(
            checks_collection.find_one_and_delete({'_id': checks_id}))
        fs.delete(checks_id)
        return presentation, checks
    else:
        return presentation, get_check(checks_id)


def get_unpassed_checks():
    return checks_collection.find({'is_passbacked': False})


def set_passbacked_flag(checks_id, flag):
    upd_check = {"$set": {'is_passbacked': flag,
                          'lms_passback_time': datetime.now(timezone.utc)}}
    check = checks_collection.update_one({'_id': checks_id}, upd_check)
    return check if check else None


def get_latest_users_check():
    return db.checks.aggregate([
        {'$sort': {'_id': -1}},
        {'$group': {'_id': '$user', 'check_id': {'$first': '$_id'}}}
    ])


def get_latest_user_check_by_moodle(moodle_id):
    return list(db.checks.find(
        {'lms_user_id': moodle_id}
    ).sort('_id', -1).limit(1))


def get_latest_check_cursor(filter, *args, **kwargs):
    checks = [result['check_id'] for result in get_latest_users_check()]
    filter['_id'] = {'$in': checks}
    return get_checks_cursor(filter, *args, **kwargs)


# Return no of bytes stored in gridfs
def get_storage():
    files = db.fs.files.find()
    ct = 0
    for file in files:
        ct += file['length']

    return ct


def get_all_checks():
    return checks_collection.find()

# get checks cursor with specified parameters


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


def get_logs_cursor(filter={}, limit=10, offset=0, sort=None, order=None):
    sort = 'serviceName' if sort == 'service-name' else sort

    count = logs_collection.count_documents(filter)
    rows = logs_collection.find(filter)

    if sort and order in ("asc, desc"):
        rows = rows.sort(sort, pymongo.ASCENDING if order ==
                         "asc" else pymongo.DESCENDING)

    rows = rows.skip(offset) if offset else rows
    rows = rows.limit(limit) if limit else rows

    return rows, count

# Get stats for one user, return a list in the form
# [check_id, login, time of check_id's creation, result(0/1)]


def get_user_checks(login):
    return checks_collection.find({'user': login})


def get_check_stats(oid):
    return checks_collection.find_one({'_id': oid})


def format_check(check):
    grade_passback_time = check['lms_passback_time']
    grade_passback_ts = grade_passback_time.strftime(
        "%H:%M:%S - %b %d %Y") if grade_passback_time else '-'
    return (str(check['_id']), check['user'], check['filename'], check['_id'].generation_time.strftime("%H:%M:%S - %b %d %Y"),
            grade_passback_ts, check['score'])


def format_stats(stats):
    return (format_check(check) for check in stats)


# LTI
class ConsumersDBManager:

    @staticmethod
    def add_consumer(consumer_key, consumer_secret, timestamp_and_nonce=[]):
        consumer = Consumers()
        consumer.consumer_key = consumer_key
        consumer.consumer_secret = consumer_secret
        if consumers_collection.find_one({'consumer_key': consumer_key}) is not None:
            return None
        else:
            consumers_collection.insert_one(consumer.pack())
            return consumer

    @staticmethod
    def get_secret(key):
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            return consumer.get('consumer_secret')
        else:
            return None

    @staticmethod
    def is_key_valid(key):
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            return True
        else:
            return False

    @staticmethod
    def has_timestamp_and_nonce(key, timestamp, nonce):
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            entries = consumer.get('timestamp_and_nonce')
            return (timestamp, nonce) in entries
        else:
            return False

    @staticmethod
    def add_timestamp_and_nonce(key, timestamp, nonce):
        upd_consumer = {"$push": {'timestamp_and_nonce': (timestamp, nonce)}}
        consumer = consumers_collection.update_one(
            {'consumer_key': key}, upd_consumer)
        return consumer if consumer else None


def add_log(timestamp, serviceName, levelname, levelno, message,
            pathname, filename, funcName, lineno):
    args = locals()
    new_log = Logs(args)
    logs_collection.insert_one(new_log.pack())
    return new_log
