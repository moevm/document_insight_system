from datetime import datetime

from app.db.db_methods import get_criteria_pack_collection
from app.db.methods.client import get_client, get_db, get_fs

# from app.db.types. import Logs

# client = get_client()
db = get_db()
fs = get_fs()

criteria_pack_collection = get_criteria_pack_collection()


def get_criteria_pack(name):
    return criteria_pack_collection.find_one({'name': name})


def save_criteria_pack(pack_info):
    """
    pack_info - dict, that includes name, raw_criterions, file_type, min_score
    """
    pack_info['updated'] = datetime.now()
    return criteria_pack_collection.update_one({'name': pack_info.get('name')}, {'$set': pack_info}, upsert=True)


def get_criterion_pack_list():
    return criteria_pack_collection.find()
