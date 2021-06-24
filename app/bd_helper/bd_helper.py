from os.path import basename
from gridfs import GridFSBucket, NoFile
from pymongo import MongoClient
from bson import ObjectId

from app.bd_helper.bd_types import User, Presentation, Checks

from datetime import datetime

from logging import getLogger
logger = getLogger('root')

client = MongoClient("mongodb://mongodb:27017")
db = client['pres-parser-db']
fs = GridFSBucket(db)

users_collection = db['users']
presentations_collection = db['presentations']
checks_collection = db['checks']


def get_client():
    return client


# Returns user if user was created and None if already exists
def add_user(username, password_hash):
    user = User()
    user.username = username
    user.password_hash = password_hash
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

disabled_parameters = ['_id', 'score', 'filename', 'user']  #extend if non-criteria parameters are added to Checks

def get_numerical_score(all_checks, disabled_parameters):
    enabled_checks = {key: all_checks[key] for key in all_checks if key not in disabled_parameters}
    enabled_value = len([check for check in enabled_checks.values() if check != -1])
    numerical_score = 0
    for check in enabled_checks.values():
        try:
            if check != -1 and check['pass']:
                numerical_score += 1
        except TypeError:
            logger.error('Try checking the disabled_parameters list, there might be a missing value')
            pass

    return (numerical_score, enabled_value)

#Get stats for one user, return a list in the form
#[check_id, login, time of check_id's creation, result(0/1)]
#TODO : add lti/missing params from #80
def get_stats(user, login):
    presentations = user['presentations']
    final = []
    for presentation in presentations:
        id_presentation = ObjectId(presentation)
        pr_obj = presentations_collection.find_one({'_id': id_presentation})
        filename = pr_obj['name']
        for checks in pr_obj['checks']:
            id_check = ObjectId(checks)
            time_added = checks.generation_time
            result = get_check(id_check)
            all_checks = vars(result)
            score = get_numerical_score(all_checks, disabled_parameters)
            final.append([str(id_check), login, filename, time_added.strftime("%H:%M:%S - %b %d %Y"), score])

    return final



def get_stats_for_one_submission(oid, login):
    checks = checks_collection.find_one({'_id': oid})
    pr_obj = presentations_collection.find_one({'checks': oid})
    filename = pr_obj['name']
    time_added = checks['_id'].generation_time
    result =  get_check(oid)
    all_checks = vars(result)
    score = get_numerical_score(all_checks, disabled_parameters)
    return [str(oid), login, filename, time_added.strftime("%H:%M:%S - %b %d %Y"), score]
