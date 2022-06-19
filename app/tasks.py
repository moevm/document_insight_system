import os
from logging import getLogger

from celery import Celery

from db import db_methods
from db.db_methods import get_user
from db.db_types import Check
from main.checker import check, check_report
from main.parser import parse

TASK_RETRY_COUNTDOWN = 10  # default = 3 * 60
logger = getLogger('root_logger')

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="create_task", bind=True)
def create_task(self, check_info):
    try:
        check_obj = Check(check_info)
        file = db_methods.get_file_by_check(check_obj._id)
        user = get_user(check_obj.user)
        check_function = check_report if check_obj.file_type == 'report' else check
        updated_check = check_function(parse(file), check_obj, file.name, user)
        updated_check.is_ended = True
        db_methods.update_check(updated_check)  # save to db
        db_methods.mark_celery_task_as_finished(self.request.id)
        return str(updated_check._id)
    except Exception as e:
        if self.request.retries == self.max_retries:
            logger.error(f"\tДостигнуто максимальное количество попыток перезапуска. Удаление задачи из очереди",
                         exc_info=True)
            db_methods.mark_celery_task_as_finished(self.request.id)
            updated_check = Check(check_info)
            updated_check.is_failed = True
            updated_check.is_ended = True
            db_methods.update_check(updated_check)  # save to db
            return 'Not OK, error: {}'.format(e)
        logger.error(f"\tПри обработке произошла ошибка: {e}. Попытка повторного запуска", exc_info=True)
        self.retry(countdown=TASK_RETRY_COUNTDOWN)  # Retry the task, adding it to the back of the queue.
