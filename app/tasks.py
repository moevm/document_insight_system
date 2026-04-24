from configparser import ConfigParser
import os
from os.path import join, exists

from celery import Celery
from celery.signals import worker_ready

from passback_grades import run_passback
from db import db_methods
from db.db_types import Check
from main.checker import check
from main.parser import parse
from check_log_context import check_log_context, current_check_stage
from root_logger import get_root_logger

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
    with check_log_context(check_id):
        paths = (original_filepath, pdf_filepath)
        remove_uploaded_files = False
        try:
            current_check_stage.set("parse")
            logger.info("Пайплайн проверки: начало парсинга файла")
            parsed = parse(original_filepath, pdf_filepath)
            current_check_stage.set("check")
            logger.info("Пайплайн проверки: парсинг завершён, запуск критериев")
            updated_check = check(parsed, check_obj)
            current_check_stage.set("persist")
            logger.info("Пайплайн проверки: критерии завершены, сохранение результата")
            updated_check.is_ended = True
            updated_check.is_failed = False
            db_methods.update_check(updated_check)  # save to db
            db_methods.mark_celery_task_as_finished(self.request.id)
            remove_uploaded_files = True
            return updated_check.pack(to_str=True)
        except Exception as e:
            current_check_stage.set("error")
            if self.request.retries == MAX_TASK_RETRIES:
                logger.error(f"\tДостигнуто максимальное количество попыток перезапуска. Удаление задачи из очереди",
                             exc_info=True)
                db_methods.mark_celery_task_as_finished(self.request.id)
                updated_check = Check(check_info)
                updated_check.is_failed = True
                updated_check.is_ended = True
                db_methods.update_check(updated_check)  # save to db
                remove_uploaded_files = True
                return 'Not OK, error: {}'.format(e)
            logger.error(f"\tПри обработке произошла ошибка: {e}. Попытка повторного запуска", exc_info=True)
            self.retry(countdown=TASK_RETRY_COUNTDOWN)  # Retry the task, adding it to the back of the queue.
        finally:
            if remove_uploaded_files:
                remove_files(paths)


@celery.task(name="convert_to_pdf", queue="convert-pdf", bind=True, retry_kwargs={'max_retries': 3})
def convert_check_file_to_pdf(self, check_obj, filepath):
    try:
        filename = check_obj['filename']
        pdf_id = check_obj['conv_pdf_fs_id']
        db_methods.write_pdf(filename, filepath, pdf_id)
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
