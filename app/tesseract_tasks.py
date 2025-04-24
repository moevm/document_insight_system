import os
import time
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded, MaxRetriesExceededError
import pytesseract
import cv2
import numpy as np
from root_logger import get_root_logger
from db import db_methods
import re
from bson import ObjectId
from main.check_packs.pack_config import BASE_REPORT_CRITERION

TASK_RETRY_COUNTDOWN = 30
SOFT_TIME_LIMIT_FOR_CALLBACK = 30
MAX_RETRIES = 1
TASK_SOFT_TIME_LIMIT = 120

logger = get_root_logger('tesseract_tasks')

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

celery.conf.timezone = 'Europe/Moscow'

TESSERACT_CONFIG = {
    'lang': 'rus+eng',
    'config': '--psm 6',
}

@celery.task(name="tesseract_recognize", queue='tesseract-queue', bind=True, max_retries=MAX_RETRIES, soft_time_limit=TASK_SOFT_TIME_LIMIT)
def tesseract_recognize(self, check_id, symbols_set, max_symbols_percentage, max_text_density):
    try:
        images = db_methods.get_images(check_id)
        if images:
            for image in images:
                image_array = np.frombuffer(image.image_data, dtype=np.uint8)
                img_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if img_cv is None:
                    raise ValueError(f"Не удалось декодировать изображение с подписью '{image.caption}' из двоичных данных")
                text = image.text
                if not text:
                    text = pytesseract.image_to_string(img_cv, **TESSERACT_CONFIG)
                if text.strip():
                    logger.info(f"Текст успешно распознан для изображения с подписью '{image.caption}'")
                else:
                    logger.info(f"Текст для изображения с подписью '{image.caption}' пустой.")
                try:
                    db_methods.add_image_text(image._id, (re.sub(r'\s+', ' ', text)).strip())
                except Exception as e:
                    raise ValueError(f"Ошибка при сохранении текста для изображения с подписью '{image.caption}': {e}")
            try:
                update_ImageTextCheck(check_id, symbols_set, max_symbols_percentage, max_text_density)
            except Exception as e:
                raise ValueError(f"Ошибка во время проверки текста: {e}")
    except SoftTimeLimitExceeded:
        logger.warning(f"Превышен мягкий лимит времени для check_id: {check_id}. Задача будет перезапущена.")
        try:
            self.retry(countdown=TASK_RETRY_COUNTDOWN)
        except MaxRetriesExceededError:
            logger.error(f"Достигнут лимит повторных попыток для check_id: {check_id}")
            add_tesseract_result(check_id, [[f"Превышен лимит времени и попыток"], 0])
    except Exception as e:
        logger.error(f"Ошибка при распознавании текста для check_id: {check_id}: {e}", exc_info=True)
        try:
            self.retry(countdown=TASK_RETRY_COUNTDOWN)
        except MaxRetriesExceededError:
            logger.error(f"Достигнут лимит повторных попыток для check_id: {check_id}")
            add_tesseract_result(check_id,[[f"Ошибка при распознавании текста: {e}"], 0])


@celery.task(name="callback_task", queue='callback-queue', soft_time_limit=SOFT_TIME_LIMIT_FOR_CALLBACK)
def callback_task(result, check_id):
    try:
        time.sleep(10)
        check = db_methods.get_check(ObjectId(check_id))
        if db_methods.get_celery_task_status_by_check(check_id):
            if check.is_ended:
                logger.info(f"Проверка успешно завершена для check_id: {check_id}")
                return
            update_tesseract_criteria_result(check)
            db_methods.update_check(check)
            logger.info(f"Проверка успешно обновлена для check_id: {check_id}")
            return
        else:
            logger.info(f"Задачи create_task и tesseract_recognize для check_id: {check_id} обрабатываются корректно. Состояние гонки исключено.")
            return
    except SoftTimeLimitExceeded:
        logger.warning(f"Превышен мягкий лимит времени для callback_task с check_id: {check_id}.")
    except Exception as e:
        logger.error(f"Ошибка в callback_task для check_id: {check_id}: {e}")


def update_ImageTextCheck(check_id, symbols_set, max_symbols_percentage, max_text_density):
    images = db_methods.get_images(check_id)
    deny_list = []
    for image in images:
        width, height = image.image_size
        text_density = calculate_text_density(image.text, width * height)
        if text_density > max_text_density:
            deny_list.append(
                f"Изображение с подписью '{image.caption}' имеет слишком высокую плотность текста: "
                f"{text_density:.2f} (максимум {max_text_density:.2f}). Это может означать, что текст нечитаем.<br>"
            )
        symbols_count = count_symbols_in_text(image.text, symbols_set)
        text_length = len(image.text)
        symbols_percentage = (symbols_count / text_length) * 100
        if symbols_percentage > max_symbols_percentage:
            deny_list.append(
                f"На изображении с подписью '{image.caption}' содержится слишком много неверно распознанных символов: "
                f"{symbols_percentage:.2f}% (максимум {max_symbols_percentage:.2f}%). Это может означать, что размер шрифта слишком маленький или текст нечитаем.<br>"
            )
    if deny_list:
        result = [[f'Проблемы с текстом на изображениях! <br>{"".join(deny_list)}'], 0]
    else:
        result = [['Текст на изображениях корректен!'], 1]
    add_tesseract_result(check_id, result)


def add_tesseract_result(check_id, result):
    updated_check = db_methods.get_check(ObjectId(check_id))
    db_methods.mark_celery_tesseract_task_as_finished_by_check(check_id, result)
    if db_methods.get_celery_task_status_by_check(check_id):
        update_tesseract_criteria_result(updated_check)
    db_methods.update_check(updated_check)


def update_tesseract_criteria_result(check):
    tesseract_task = db_methods.get_celery_tesseract_task_by_check(str(check._id))
    for criteria in check.enabled_checks:
        if criteria["id"] == 'image_text_check':
            criteria["verdict"] = tesseract_task['tesseract_result'][0]
            criteria["score"] = tesseract_task['tesseract_result'][1]
            check.score = round(check.score - (1 - tesseract_task['tesseract_result'][1]) / len(BASE_REPORT_CRITERION), 3)
            check.is_ended = True
            return


def count_symbols_in_text(text, symbols_set):
    return sum(1 for char in text if char in symbols_set)


def calculate_text_density(text, image_area):
    text_without_spaces = ''.join(text.split())
    if image_area == 0:
        return 0
    return len(text_without_spaces) / image_area