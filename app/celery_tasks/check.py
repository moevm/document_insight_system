import logging.config
import os
from os.path import exists, join

from celery import Celery
from celery.signals import worker_ready
from check_log_context import check_log_context, current_check_stage
from main.checker import check
from main.parser import parse
from main.reports.parse_file import parse_file
from passback_grades import run_passback
from root_logger import get_root_logger

from app.celery_tasks.config import (
    APP_DIR,
    CELERY_BEAT_SCHEDULE,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CELERY_TIMEZONE,
    CHECK_MAX_TASK_RETRIES,
    CHECK_TASK_RETRY_COUNTDOWN,
    FILES_FOLDER,
)
from app.celery_tasks.tesseract import update_tesseract_criteria_result
from app.db.methods import celery_check as celery_check_methods
from app.db.methods import celery_tesseract as celery_tesseract_methods
from app.db.methods import check as check_methods
from app.db.methods import file as file_methods
from app.db.methods import parsed_text as parsed_text_methods
from app.db.types.Check import Check
from app.db.types.ParsedText import ParsedText

logging_config = APP_DIR / "logging.conf"
if logging_config.is_file():
    logging.config.fileConfig(logging_config, disable_existing_loggers=False)

logger = get_root_logger('tasks')

celery = Celery(__name__)
celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND
celery.conf.beat_schedule = CELERY_BEAT_SCHEDULE
celery.conf.timezone = CELERY_TIMEZONE


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
            document_id = parsed_text_methods.get_or_create_parsed_text_id(check_info['filename'])
            parsed = parse(original_filepath, pdf_filepath, check_id, document_id)
            parsed.make_chapters(check_obj.file_type['report_type'])
            parsed.make_headers(check_obj.file_type['report_type'])
            chapters = parse_file.chapters_to_sections(parsed)
            current_check_stage.set("check")
            logger.info("Пайплайн проверки: парсинг завершён, запуск критериев")
            updated_check = check(parsed, check_obj)
            parsed_text = ParsedText(filename=check_info['filename'])
            parsed_text.parsed_chapters = parse_file.attach_pages_and_images_to_sections(chapters, parsed)
            parsed_text_methods.save_parsed_text(check_id, parsed_text, document_id)
            if celery_tesseract_methods.get_celery_tesseract_task_status_by_check(check_id):
                update_tesseract_criteria_result(updated_check)
            current_check_stage.set("persist")
            logger.info("Пайплайн проверки: критерии завершены, сохранение результата")
            updated_check.is_ended = True
            updated_check.is_failed = False
            check_methods.update_check(updated_check)  # save to db
            celery_check_methods.mark_celery_task_as_finished(self.request.id)
            remove_uploaded_files = True
            return updated_check.pack(to_str=True)
        except Exception as e:
            current_check_stage.set("error")
            if self.request.retries == CHECK_MAX_TASK_RETRIES:
                logger.error(
                    "\tДостигнуто максимальное количество попыток перезапуска. Удаление задачи из очереди",
                    exc_info=True,
                )
                celery_check_methods.mark_celery_task_as_finished(self.request.id)
                updated_check = Check(check_info)
                updated_check.is_failed = True
                updated_check.is_ended = True
                check_methods.update_check(updated_check)  # save to db
                remove_uploaded_files = True
                return 'Not OK, error: {}'.format(e)
            logger.error(f"\tПри обработке произошла ошибка: {e}. Попытка повторного запуска", exc_info=True)
            self.retry(countdown=CHECK_TASK_RETRY_COUNTDOWN)  # Retry the task, adding it to the back of the queue.
        finally:
            if remove_uploaded_files:
                remove_files(paths)


@celery.task(name="convert_to_pdf", queue="convert-pdf", bind=True, retry_kwargs={'max_retries': 3})
def convert_check_file_to_pdf(self, check_obj, filepath, rewrite=False):
    try:
        filename = check_obj['filename']
        pdf_id = check_obj['conv_pdf_fs_id']
        file_methods.write_pdf(filename, filepath, pdf_id, rewrite=rewrite)
        return check_obj
    except Exception as e:
        logger.error(
            f"При конвертации файла произошла ошибка: {e}. Следующая попытка через {CHECK_TASK_RETRY_COUNTDOWN}",
            exc_info=True,
        )
        raise self.retry(countdown=CHECK_TASK_RETRY_COUNTDOWN) from e


@celery.task(name="passback-task", queue='passback-grade')
def passback_task():
    return run_passback()


def remove_files(filepaths):
    for filepath in filepaths:
        if exists(filepath):
            os.remove(filepath)
