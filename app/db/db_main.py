from app.db.methods.client import get_client, get_db, get_fs

client = get_client()
db = get_db()
fs = get_fs()

users_collection = db['users']
files_info_collection = db['presentations']  # actually, collection for all files (pres and reports)
checks_collection = db['checks']
consumers_collection = db['consumers']
criteria_pack_collection = db['criteria_pack']
logs_collection = db.create_collection(
    'logs', capped=True, size=5242880) if not db['logs'] else db['logs']
celery_check_collection = db['celery_check']  # collection for mapping celery_task to check


def get_checks_collection():
    return checks_collection


def get_users_collection():
    return users_collection


def get_criteria_pack_collection():
    return criteria_pack_collection


def get_files_info_collection():
    return files_info_collection


def get_logs_collection():
    return logs_collection


def get_celery_check_collection():
    return celery_check_collection
