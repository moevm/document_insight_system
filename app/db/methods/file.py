from app.db.db_main import get_files_info_collection, get_users_collection
from app.db.methods.client import get_client, get_db, get_fs
from os.path import basename
from bson import ObjectId
from gridfs import NoFile, errors as gridfs_errors
from pymongo import errors as pymongo_errors
from app.utils.converter import convert_to

from app.db.types.Presentation import Presentation
from app.db.methods.edit_user import edit_user
from app.db.methods.check import delete_check

client = get_client()
db = get_db()
fs = get_fs()

files_info_collection = get_files_info_collection()  # actually, collection for all files (pres and reports)

users_collection = get_users_collection()


def add_file_info_and_content(username, filepath, file_type, file_id=None):
    if not file_id:
        file_id = ObjectId()
    # parsed_file's info
    filename = basename(filepath)
    file_info = Presentation({
        '_id': file_id,
        'name': filename,
        'file_type': file_type
    })
    file_info_id = files_info_collection.insert_one(file_info.pack()).inserted_id
    assert file_id == file_info_id, f"{file_id} -- {file_info_id}"
    # parsed_file's content in GridFS (file_id = file_info_id)
    add_file_to_db(filename, filepath, file_info_id)
    # add parsed_file to user info
    users_collection.update_one({'username': username}, {"$push": {'files': file_info_id}})
    return file_info_id


# Returns presentations with given id or None
def get_presentation(file_id):
    file = files_info_collection.find_one({'_id': file_id})
    if file is not None:
        return Presentation(file)
    else:
        return None


# Returns files of given user with given id or None
def find_presentation(user, presentation_name):
    files = []
    for presentation_id in user.files:
        files.append(get_presentation(presentation_id))
    presentation = next(
        (x for x in files if x.name == presentation_name), None)
    if presentation is not None:
        return presentation
    else:
        return None


# Deletes files with given id, deleting also its checks, returns files
def delete_presentation(user, presentation_id):
    if presentation_id in user.files:
        user.files.remove(presentation_id)
        edit_user(user)
        presentation = get_presentation(presentation_id)
        for check_id in presentation.checks:
            presentation, check = delete_check(presentation, check_id)
        presentation = Presentation(
            files_info_collection.find_one_and_delete({'_id': presentation_id}))
        return user, presentation
    else:
        return user, get_presentation(presentation_id)


def get_pdf_id(file_id=None):
    if not file_id: file_id = ObjectId()
    return file_id


def write_pdf(filename, filepath, file_id=None, rewrite=False):
    converted_filepath = convert_to(filepath, target_format="pdf")
    return add_file_to_db(filename, converted_filepath, file_id, rewrite=rewrite)



def add_file_to_db(filename, filepath, file_id=None, rewrite=False):
    def write_file(filename, filepath, file_id):
        with open(filepath, "rb") as file:
            fs.upload_from_stream_with_id(file_id, filename, file)

    if not file_id:
        file_id = ObjectId()
    elif type(file_id) is str:
        file_id = ObjectId(file_id)
    try:
        write_file(filename, filepath, file_id)
        return file_id
    except (pymongo_errors.DuplicateKeyError, gridfs_errors.FileExists) as exc:
        if rewrite:
            fs.delete(file_id)
            write_file(filename, filepath, file_id)
            return file_id
        raise exc


def write_file_from_db_file(file_id, abs_filepath):
    with open(abs_filepath, 'wb+') as file:
        fs.download_to_stream(file_id, file)
    return True


def get_file_by_check(checks_id):
    try:
        return fs.open_download_stream(checks_id)
    except NoFile:
        return None


def find_pdf_by_file_id(file_id):
    try:
        return fs.open_download_stream(file_id)
    except NoFile:
        return None


def get_storage():
    files = db.fs.files.find()
    ct = 0
    for file in files:
        ct += file['length']

    return ct
