from datetime import datetime

from app.db.db_main import get_celery_check_collection
from app.db.methods.client import get_db

db = get_db()

celery_check_collection = get_celery_check_collection()  # collection for mapping celery_task to check


def add_celery_task(celery_task_id, check_id):
    return celery_check_collection.insert_one(
        {'celery_task_id': celery_task_id, 'check_id': check_id, 'started_at': datetime.now()}).inserted_id


def mark_celery_task_as_finished(celery_task_id, finished_time=None):
    celery_task = get_celery_task(celery_task_id)
    if not celery_task: return
    if finished_time is None: finished_time = datetime.now()
    return celery_check_collection.update_one({'celery_task_id': celery_task_id}, {
        '$set': {'finished_at': finished_time,
                 'processing_time': (finished_time - celery_task['started_at']).total_seconds()}})


def get_average_processing_time(min_time=5.0):
    # use only success check (failed checks processing time is more bigger than normal)
    result = list(celery_check_collection.aggregate([
        {'$match': {'processing_time': {'$lt': 170}}},
        {'$group': {'_id': None, 'avg_processing_time': {'$avg': "$processing_time"}}}
    ]))
    if result and result[0]['avg_processing_time']:
        result = result[0]['avg_processing_time']
        if result > min_time:
            return round(result, 1)
    return min_time


def get_celery_task(celery_task_id):
    return celery_check_collection.find_one({'celery_task_id': celery_task_id})


def get_celery_task_by_check(check_id):
    return celery_check_collection.find_one({'check_id': check_id})
