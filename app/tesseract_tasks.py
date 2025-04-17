import os
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
import pytesseract
import cv2
import numpy as np
from root_logger import get_root_logger
from db import db_methods
import re
from bson import ObjectId
from main.checks.report_checks.image_text_check import SYMBOLS_SET, MAX_SYMBOLS_PERCENTAGE, MAX_TEXT_DENSITY
from main.check_packs.pack_config import BASE_REPORT_CRITERION

TASK_RETRY_COUNTDOWN = 30
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
def tesseract_recognize(self, check_id):
    try:
        images = db_methods.get_images(check_id)
        if images:
            for image in images:
                image_array = np.frombuffer(image.image_data, dtype=np.uint8)
                img_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if img_cv is None:
                    raise ValueError("Не удалось декодировать изображение из двоичных данных")
                text = image.text
                if not text:
                    text = pytesseract.image_to_string(img_cv, **TESSERACT_CONFIG)
                if text.strip():
                    logger.info(f"Текст успешно распознан для изображения с подписью: {image.caption}")
                else:
                    logger.info(f"Текст для изображения с подписью: {image.caption} пустой.")
                try:
                    db_methods.add_image_text(image._id, (re.sub(r'\s+', ' ', text)).strip())
                except Exception as e:
                    raise ValueError(f"Ошибка при сохранении текста для изображения с подписью: {image.caption}: {e}")
            try:
                update_ImageTextCheck(check_id)
            except Exception as e:
                raise ValueError(f"Ошибка во время проверки текста: {e}")
    except SoftTimeLimitExceeded:
        logger.warning(f"Превышен мягкий лимит времени для check_id: {check_id}. Задача будет перезапущена.")
        self.retry(countdown=TASK_RETRY_COUNTDOWN)
    except Exception as e:
        if self.request.retries >= self.max_retries:
            add_tesseract_result(check_id,[[f"Ошибка при распознавании текста: {e}"], 0])
        logger.error(f"Ошибка при распознавании текста для check_id: {check_id}: {e}", exc_info=True)
        logger.info(f"Повторная попытка распознавания для check_id: {check_id}. Попытка {self.request.retries + 1} из {self.max_retries}.")
        self.retry(countdown=TASK_RETRY_COUNTDOWN)


def update_ImageTextCheck(check_id):
    images = db_methods.get_images(check_id)
    deny_list = []
    for image in images:
        width, height = image.image_size
        text_density = calculate_text_density(image.text, width * height)
        if text_density > MAX_TEXT_DENSITY:
            deny_list.append(
                f"Изображение с подписью '{image.caption}' имеет слишком высокую плотность текста: "
                f"{text_density:.4f} (максимум {MAX_TEXT_DENSITY}). Это может означать, что текст нечитаем.<br>"
            )
        symbols_count = count_symbols_in_text(image.text)
        text_length = len(image.text)
        symbols_percentage = (symbols_count / text_length) * 100
        if symbols_percentage > MAX_SYMBOLS_PERCENTAGE:
            deny_list.append(
                f"На изображении с подписью '{image.caption}' содержится слишком много неверно распознанных символов: "
                f"{symbols_percentage:.2f}% (максимум {MAX_SYMBOLS_PERCENTAGE}%). Это может означать, что размер шрифта слишком маленький или текст нечитаем.<br>"
            )
    if deny_list:
        result = [[f'Проблемы с текстом на изображениях! <br>{"".join(deny_list)}'], 0]
    else:
        result = [['Текст на изображениях корректен!'], 1]
    add_tesseract_result(check_id, result)


def add_tesseract_result(check_id, result):
    updated_check = db_methods.get_check(ObjectId(check_id))
    updated_check.tesseract_result = result
    if 'processing_time' in db_methods.get_celery_task_by_check(ObjectId(check_id)):
        update_tesseract_criteria_result(updated_check)
    db_methods.update_check(updated_check)

def update_tesseract_criteria_result(check):
    for criteria in check.enabled_checks:
        if criteria["id"] == 'image_text_check':
            criteria["verdict"] = check.tesseract_result[0]
            criteria["score"] = check.tesseract_result[1]
            check.score = round(check.score - (1 - check.tesseract_result[1]) / len(BASE_REPORT_CRITERION), 3)
            check.is_ended = True
            return

def count_symbols_in_text(text):
    return sum(1 for char in text if char in SYMBOLS_SET)

def calculate_text_density(text, image_area):
    text_without_spaces = ''.join(text.split())
    if image_area == 0:
        return 0
    return len(text_without_spaces) / image_area