import os
from logging import getLogger

from celery import Celery

from db import db_methods
from db.db_methods import get_user
from db.db_types import Check
from main.checker import check
from main.parser import parse

logger = getLogger('root')

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="create_task")
def create_task(check_info):
    try:
        check_obj = Check(check_info)
        file = db_methods.get_file_by_check(check_obj._id)
        updated_check = check(parse(file), check_obj, file.name, get_user(check_obj.user))
        db_methods.update_check(updated_check)  # save to db
        return updated_check.pack(to_str=True)
    except Exception as e:
        logger.error("\tПри обработке произошла ошибка: " + str(e), exc_info=True)
        return 'Not OK, error: {}'.format(e)
