from datetime import datetime

from app.db.db_main import get_celery_tesseract_collection

celery_tesseract_collection = get_celery_tesseract_collection()


def add_celery_tesseract_task(celery_tesseract_task_id, check_id):
    return celery_tesseract_collection.insert_one(
        {'celery_tesseract_task_id': celery_tesseract_task_id, 'check_id': check_id, 'started_at': datetime.now()}
    ).inserted_id


def get_celery_tesseract_task(celery_tesseract_task_id):
    return celery_tesseract_collection.find_one({'celery_tesseract_task_id': celery_tesseract_task_id})


def get_celery_tesseract_task_by_check(check_id):
    return celery_tesseract_collection.find_one({'check_id': str(check_id)})


def get_celery_tesseract_task_status_by_check(check_id):
    celery_tesseract_task = get_celery_tesseract_task_by_check(check_id)
    if celery_tesseract_task and 'finished_at' in celery_tesseract_task:
        return True
    return False


def mark_celery_tesseract_task_as_finished_by_check(check_id, tesseract_result, finished_time=None):
    celery_tesseract_task = get_celery_tesseract_task_by_check(check_id)
    if not celery_tesseract_task:
        return
    if finished_time is None:
        finished_time = datetime.now()
    return celery_tesseract_collection.update_one(
        {'check_id': check_id},
        {
            '$set': {
                'finished_at': finished_time,
                'tesseract_result': tesseract_result,
                'processing_time': (finished_time - celery_tesseract_task['started_at']).total_seconds(),
            }
        },
    )
