from os.path import basename
from gridfs import GridFSBucket, NoFile
from pymongo import MongoClient
from bson import ObjectId
import pymongo

from app.bd_helper.bd_types import User, Presentation, Checks, Consumers, Sessions

from datetime import datetime

from logging import getLogger
logger = getLogger('root')

client = MongoClient("mongodb://mongodb:27017")
db = client['pres-parser-db']
fs = GridFSBucket(db)

users_collection = db['users']
presentations_collection = db['presentations']
checks_collection = db['checks']
consumers_collection = db['consumers']
sessions_collection = db['sessions']


def get_client():
    return client


# Returns user if user was created and None if already exists
def add_user(username, password_hash = '', is_LTI = False):
    user = User()
    user.username = username
    if not is_LTI:
        user.password_hash = password_hash
        user.is_LTI = is_LTI
    else:
        user.is_LTI = is_LTI
    if users_collection.find_one({'username': username}) is not None:
        return None
    else:
        users_collection.insert_one(user.pack())
        return user


# Returns user if there was user with given credentials and None if not
def validate_user(username, password_hash):
    user = users_collection.find_one({'username': username, 'password_hash': password_hash})
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
    presentation_id = presentations_collection.insert_one(presentation.pack()).inserted_id
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
    presentation = next((x for x in presentations if x.name == presentation_name), None)
    if presentation is not None:
        return presentation
    else:
        return None


def __edit_presentation(presentation):
    if presentations_collection.find_one_and_replace({'_id': presentation._id}, presentation.pack()) is not None:
        return True
    else:
        return False


# Deletes presentation with given id, deleting also its checks, returns presentation
def delete_presentation(user, presentation_id):
    if presentation_id in user.presentations:
        user.presentations.remove(presentation_id)
        edit_user(user)
        presentation = get_presentation(presentation_id)
        for check_id in presentation.checks:
            presentation, check = delete_check(presentation, check_id)
        presentation = Presentation(presentations_collection.find_one_and_delete({'_id': presentation_id}))
        return user, presentation
    else:
        return user, get_presentation(presentation_id)


# Creates checks from given user check-list
def create_check(user):
    return Checks(user.criteria.pack())


# Adds checks to given presentation, updates presentation, returns presentation and checks id
def add_check(presentation, checks, presentation_file):
    checks_id = checks_collection.insert_one(checks.pack()).inserted_id
    presentation.checks.append(checks_id)
    __edit_presentation(presentation)

    grid_in = fs.open_upload_stream_with_id(checks_id, basename(presentation_file))
    grid_in.write(open(presentation_file, 'rb'))
    grid_in.close()

    return presentation, checks_id


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


# Deletes checks with given id, returns presentation
def delete_check(presentation, checks_id):
    if checks_id in presentation.checks:
        presentation.checks.remove(checks_id)
        __edit_presentation(presentation)
        checks = Checks(checks_collection.find_one_and_delete({'_id': checks_id}))
        fs.delete(checks_id)
        return presentation, checks
    else:
        return presentation, get_check(checks_id)


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
    count = checks_collection.count_documents(filter)
    rows = checks_collection.find(filter)

    if sort and order in ("asc, desc"):
        rows = rows.sort(sort, pymongo.ASCENDING if order == "asc" else pymongo.DESCENDING)

    rows = rows.skip(offset) if offset else rows
    rows = rows.limit(limit) if limit else rows

    return rows, count


#Get stats for one user, return a list in the form
#[check_id, login, time of check_id's creation, result(0/1)]
#TODO : add lti/missing params from #80
def get_user_checks(login):
    return checks_collection.find({'user': login})


def get_check_stats(oid):
    return checks_collection.find_one({'_id': oid})

def format_check(check):
    return (str(check['_id']), check['user'], check['filename'], check['_id'].generation_time.strftime("%H:%M:%S - %b %d %Y"),
                    check['score'])

def format_stats(stats):
    return (format_check(check) for check in stats)


#LTI
class ConsumersDBManager:

    @staticmethod
    def add_consumer(consumer_key, consumer_secret, timestamp_and_nonce = []):
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
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            consumer.get('timestamp_and_nonce').append((timestamp, nonce))
            upd_consumer = Consumers(consumer)
            consumers_collection.find_one_and_replace({'consumer_key': key}, upd_consumer.pack())
            return consumer
        else:
            return None

class SessionsDBManager:

    @staticmethod
    def add_session(session_id, task, params_for_passback, admin=False):
        existing_session = sessions_collection.find_one({'session_id ': session_id})
        task_info = {task: {'params_for_passback': params_for_passback}}
        new_session = Sessions()
        new_session.session_id = session_id
        new_session.tasks = task_info
        new_session.is_admin = admin

        if existing_session is not None:
            existing_session.tasks = task_info
            existing_session.is_admin = admin
            upd_session = Sessions(existing_session)
            sessions_collection.find_one_and_replace({'session_id ': session_id}, upd_session.pack())
        else:
            sessions_collection.insert_one(new_session.pack())

    @staticmethod
    def get_session(session_id):
        session = sessions_collection.find_one({'session_id ': session_id})
        if session is not None:
            return Session(session)
        else:
            return None
