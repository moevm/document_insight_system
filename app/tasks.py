import os
import time
from celery import Celery
from app.bd_helper.bd_types import Checks
from os.path import join, exists
from bson import ObjectId

from app.bd_helper.bd_helper import *
from app.main.checker import check
from app.main.parser import parse

import os
from logging import getLogger
logger = getLogger('root')

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

@celery.task(name="create_task")
def create_task(filename, converted_id):
    try:
        delete = True
        presentation_name = basename(filename)
        #presentation = find_presentation(current_user, presentation_name)
        #if presentation is None:
        #    user, presentation_id = add_presentation(current_user, presentation_name)
        #    presentation = get_presentation(presentation_id)

        checks = Checks({})

        checks.conv_pdf_fs_id = ObjectId(converted_id)
        check(parse(filename), checks, presentation_name)
        checks_id = add_check(checks, filename)

        os.remove(filename)

        return str(checks_id)
    except Exception as e:
        logger.error("\tПри обработке произошла ошибка: " + str(e), exc_info=True)
        return 'Not OK, error: {}'.format(e)
