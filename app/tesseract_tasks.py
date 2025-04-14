import os
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from celery.signals import worker_ready
import pytesseract
import cv2
import numpy as np
from root_logger import get_root_logger
from db import db_methods
import re
from .main.checks.report_checks.image_text_check import SYMBOLS_SET, MAX_SYMBOLS_PERCENTAGE, MAX_TEXT_DENSITY

TASK_RETRY_COUNTDOWN = 60
MAX_RETRIES = 2
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

@worker_ready.connect
def at_start(sender, **k):
    logger.info("Tesseract worker is ready!")

@celery.task(name="tesseract_recognize", queue='tesseract-queue', bind=True, max_retries=MAX_RETRIES, soft_time_limit=TASK_SOFT_TIME_LIMIT)
def tesseract_recognize(self, check_id):
    try:
        images = db_methods.get_images(check_id)
        for image in images:
            image_array = np.frombuffer(image.image_data, dtype=np.uint8)
            img_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if img_cv is None:
                raise ValueError("Не удалось декодировать изображение из двоичных данных")
            text = pytesseract.image_to_string(img_cv, **TESSERACT_CONFIG)
            if text is None:
                logger.warning(f"Tesseract вернул None для image_id: {image._id}.")
                text = ""
            logger.info(f"Текст успешно распознан для image_id: {image._id}")
            
            text = (re.sub(r'\s+', ' ', text)).strip()
            db_methods.add_image_text(image._id, text)
        update_ImageTextCheck(check_id)
        
    except SoftTimeLimitExceeded:
        logger.warning(f"Превышен мягкий лимит времени для check_id: {check_id}. Задача будет перезапущена.")
        self.retry(countdown=TASK_RETRY_COUNTDOWN)
    except Exception as e:
        logger.error(f"Ошибка при распознавании текста: {e}", exc_info=True)
        logger.info(f"Пустая строка записана для check_id: {check_id} из-за ошибки: {e}")
        if self.request.retries >= self.max_retries:
            logger.error(f"Достигнуто максимальное количество попыток для check_id: {check_id}")
            return f"Ошибка: {e}"
        logger.info(f"Повторная попытка распознавания для check_id: {check_id}. Попытка {self.request.retries + 1} из {self.max_retries}.")
        self.retry(countdown=TASK_RETRY_COUNTDOWN)


def update_ImageTextCheck(check_id):
    updated_check = db_methods.get_check(check_id)
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
        update_criteria_result(updated_check, 'image_quality_check', [f'Проблемы с текстом на изображениях! <br>{"".join(deny_list)}'], 0)
    else:
        update_criteria_result(updated_check, 'image_quality_check', ['Текст на изображениях корректен!'], 1)
    db_methods.update_check(updated_check)

def update_criteria_result(check, criteria_id, new_verdict, new_score):
    for criteria in check.enabled_checks:
        if criteria["id"] == criteria_id:
            criteria["verdict"] = new_verdict
            criteria["score"] = new_score
            return True
    return False

def count_symbols_in_text(text):
    return sum(1 for char in text if char in SYMBOLS_SET)

def calculate_text_density(text, image_area):
    text_without_spaces = ''.join(text.split())
    if image_area == 0:
        return 0
    return len(text_without_spaces) / image_area