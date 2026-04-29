from configparser import ConfigParser
import os
from os.path import join, exists

from celery import Celery
from celery.signals import worker_ready

from passback_grades import run_passback
from main.reports.pasre_file import parse_file
from db import db_methods
from db.db_types import Check, ParsedText
from main.checker import check
from main.parser import parse
from root_logger import get_root_logger
from tesseract_tasks import update_tesseract_criteria_result

config = ConfigParser()
config.read('app/config.ini')

TASK_RETRY_COUNTDOWN = 60  # default = 3 * 60
MAX_TASK_RETRIES = 3
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


@worker_ready.connect
def at_start(sender, **k):

    from nltk import download

    download("stopwords")
    download("punkt")


@celery.task(name="create_task", queue="check-solution", bind=True)
def create_task(self, check_info):
    check_obj = Check(check_info)
    check_id = str(check_obj._id)
    # get check files filepath
    original_filepath = join(FILES_FOLDER, f"{check_id}.{check_obj.filename.rsplit('.', 1)[-1]}")
    pdf_filepath = join(FILES_FOLDER, f"{check_id}.pdf")
    try:
        parsed_file_object = parse(original_filepath, pdf_filepath, check_id)
        parsed_file_object.make_chapters(check_obj.file_type['report_type'])
        parsed_file_object.make_headers(check_obj.file_type['report_type'])
        chapters = parse_file.parse_chapters(parsed_file_object)
        
        updated_check = check(parsed_file_object, check_obj)
        updated_check.is_failed = False
        parsed_text = ParsedText(dict(filename=check_info['filename']))
        parsed_text.parsed_chapters = parse_file.parse_headers_and_pages_and_images(chapters, parsed_file_object)
        db_methods.add_parsed_text(check_id, parsed_text)
        if db_methods.get_celery_tesseract_task_status_by_check(check_id):
            update_tesseract_criteria_result(updated_check)
        db_methods.update_check(updated_check)  # save to db
        db_methods.mark_celery_task_as_finished(self.request.id)

        # remove files from FILES_FOLDER after checking
        remove_files((original_filepath, pdf_filepath))

        return updated_check.pack(to_str=True)
    except Exception as e:
        if self.request.retries == MAX_TASK_RETRIES:
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


@celery.task(name="convert_to_pdf", queue="convert-pdf", bind=True, retry_kwargs={'max_retries': 3})
def convert_check_file_to_pdf(self, check_obj, filepath, rewrite=False):
    try:
        filename = check_obj['filename']
        pdf_id = check_obj['conv_pdf_fs_id']
        db_methods.write_pdf(filename, filepath, pdf_id, rewrite=rewrite)
        return check_obj
    except Exception as e:
        logger.error(
            f"При конвертации файла произошла ошибка: {e}. Следующая попытка через {TASK_RETRY_COUNTDOWN}",
            exc_info=True,
        )
        raise self.retry(countdown=TASK_RETRY_COUNTDOWN)


@celery.task(name="passback-task", queue='passback-grade')
def passback_task():
    return run_passback()


def remove_files(filepaths):
    for filepath in filepaths:
        if exists(filepath): os.remove(filepath)
