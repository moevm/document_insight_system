import configparser
import os
from os.path import join, exists

from celery import Celery

import passback_grades
from app.main.reports.parse_file.parse_file import parse_headers_and_pages, parse_chapters
from db import db_methods
from db.db_types import Check, ParsedText
from main.checker import check
from main.parser import parse
from main.check_packs import BASE_PACKS
from root_logger import get_root_logger

config = configparser.ConfigParser()
config.read('app/config.ini')

TASK_RETRY_COUNTDOWN = 60  # default = 3 * 60
logger = get_root_logger('tasks')

FILES_FOLDER = '/usr/src/project/files'

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

celery.conf.beat_schedule = {
    'passback-grades': {
        'task': 'passback-task',
        'schedule': config.getint('consts', 'PASSBACK_TIMER'),
    },
}
celery.conf.timezone = 'Europe/Moscow'  # todo: get from env


@celery.task(name="create_task", queue='check-solution', bind=True)
def create_task(self, check_info):
    check_obj = Check(check_info)
    check_id = str(check_obj._id)
    # get check files filepath
    original_filepath = join(FILES_FOLDER, f"{check_id}.{check_obj.filename.rsplit('.', 1)[-1]}")
    pdf_filepath = join(FILES_FOLDER, f"{check_id}.pdf")
    try:
        parsed_file_object = parse(original_filepath, pdf_filepath)
        parsed_file_object.make_chapters(check_obj.file_type['report_type'])
        parsed_file_object.make_headers(check_obj.file_type['report_type'])
        chapters = parse_chapters(parsed_file_object)

        updated_check = check(parsed_file_object, check_obj)
        updated_check.is_ended = True
        updated_check.is_failed = False
        updated_check.parsed_chapters = parse_headers_and_pages(chapters, parsed_file_object)

        parsed_text = ParsedText(check_info)
        parsed_text.parsed_chapters = parse_headers_and_pages(chapters, parsed_file_object)

        db_methods.update_check(updated_check)  # save to db
        db_methods.add_parsed_text(check_id, parsed_text)
        db_methods.mark_celery_task_as_finished(self.request.id)

        # remove files from FILES_FOLDER after checking
        remove_files((original_filepath, pdf_filepath))

        return updated_check.pack(to_str=True)
    except Exception as e:
        if self.request.retries == self.max_retries:
            logger.error(f"\tДостигнуто максимальное количество попыток перезапуска. Удаление задачи из очереди",
                         exc_info=True)
            db_methods.mark_celery_task_as_finished(self.request.id)
            updated_check = Check(check_info)
            updated_check.is_failed = True
            updated_check.is_ended = True
            db_methods.update_check(updated_check)  # save to db
            # remove files from FILES_FOLDER after checking
            remove_files((original_filepath, pdf_filepath))
            return 'Not OK, error: {}'.format(e)
        logger.error(f"\tПри обработке произошла ошибка: {e}. Попытка повторного запуска", exc_info=True)
        self.retry(countdown=TASK_RETRY_COUNTDOWN)  # Retry the task, adding it to the back of the queue.


def remove_files(filepaths):
    for filepath in filepaths:
        if exists(filepath): os.remove(filepath)


@celery.task(name="passback-task", queue='passback-grade')
def passback_task():
    print('Run passback')
    return passback_grades.run_passback()
