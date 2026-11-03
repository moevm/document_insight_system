import re
import time

import cv2
import numpy as np
import pytesseract
from bson import ObjectId
from celery import Celery
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from main.check_packs.pack_config import BASE_REPORT_CRITERION
from root_logger import get_root_logger

from app.celery_tasks.config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CELERY_TIMEZONE,
    TESSERACT_CALLBACK_SOFT_TIME_LIMIT,
    TESSERACT_CONFIG,
    TESSERACT_MAX_RETRIES,
    TESSERACT_TASK_RETRY_COUNTDOWN,
    TESSERACT_TASK_SOFT_TIME_LIMIT,
)
from app.db.methods import celery_check as celery_check_methods
from app.db.methods import celery_tesseract as celery_tesseract_methods
from app.db.methods import check as check_methods
from app.db.methods import image as image_methods

logger = get_root_logger('tesseract_tasks')

celery = Celery(__name__)
celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND
celery.conf.timezone = CELERY_TIMEZONE


@celery.task(
    name="tesseract_recognize",
    queue='tesseract-queue',
    bind=True,
    max_retries=TESSERACT_MAX_RETRIES,
    soft_time_limit=TESSERACT_TASK_SOFT_TIME_LIMIT,
)
def tesseract_recognize(self, check_id, symbols_set, max_symbols_percentage, max_text_density):
    try:
        images = image_methods.get_images_by_check_id(check_id)
        if images:
            for image in images:
                image_array = np.frombuffer(image.image_data, dtype=np.uint8)
                img_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if img_cv is None:
                    raise ValueError(
                        f"Не удалось декодировать изображение с подписью '{image.caption}' из двоичных данных"
                    )
                text = image.text
                if not text:
                    text = pytesseract.image_to_string(img_cv, **TESSERACT_CONFIG)
                if text.strip():
                    logger.info(f"Текст успешно распознан для изображения с подписью '{image.caption}'")
                else:
                    logger.info(f"Текст для изображения с подписью '{image.caption}' пустой.")
                try:
                    image.text = (re.sub(r'\s+', ' ', text)).strip()
                    image_methods.update_image(image)
                except Exception as e:
                    raise ValueError(
                        f"Ошибка при сохранении текста для изображения с подписью '{image.caption}': {e}"
                    ) from e
            try:
                update_ImageTextCheck(check_id, symbols_set, max_symbols_percentage, max_text_density)
            except Exception as e:
                raise ValueError(f"Ошибка во время проверки текста: {e}") from e
    except SoftTimeLimitExceeded:
        logger.warning(f"Превышен мягкий лимит времени для check_id: {check_id}. Задача будет перезапущена.")
        try:
            self.retry(countdown=TESSERACT_TASK_RETRY_COUNTDOWN)
        except MaxRetriesExceededError:
            logger.error(f"Достигнут лимит повторных попыток для check_id: {check_id}")
            add_tesseract_result(check_id, [["Превышен лимит времени и попыток"], 0])
    except Exception as e:
        logger.error(f"Ошибка при распознавании текста для check_id: {check_id}: {e}", exc_info=True)
        try:
            self.retry(countdown=TESSERACT_TASK_RETRY_COUNTDOWN)
        except MaxRetriesExceededError:
            logger.error(f"Достигнут лимит повторных попыток для check_id: {check_id}")
            add_tesseract_result(check_id, [[f"Ошибка при распознавании текста: {e}"], 0])


@celery.task(name="callback_task", queue='callback-queue', soft_time_limit=TESSERACT_CALLBACK_SOFT_TIME_LIMIT)
def callback_task(check_id):
    try:
        time.sleep(10)
        check = check_methods.get_check(ObjectId(check_id))
        if celery_check_methods.get_celery_task_status_by_check(ObjectId(check_id)):
            if check.is_ended:
                logger.info(f"Проверка успешно завершена для check_id: {check_id}")
                return
            update_tesseract_criteria_result(check)
            check_methods.update_check(check)
            logger.info(f"Проверка успешно обновлена для check_id: {check_id}")
            return
        else:
            logger.info(f"Задачи для check_id: {check_id} обрабатываются корректно. Состояние гонки исключено.")
            return
    except SoftTimeLimitExceeded:
        logger.warning(f"Превышен мягкий лимит времени для callback_task с check_id: {check_id}.")
    except Exception as e:
        logger.error(f"Ошибка в callback_task для check_id: {check_id}: {e}")


def update_ImageTextCheck(check_id, symbols_set, max_symbols_percentage, max_text_density):
    images = image_methods.get_images_by_check_id(check_id)
    deny_list = []

    for image in images:
        text = image.text or ''
        width, height = image.image_size

        if image.text_density is None:
            image.text_density = calculate_text_density(text, width * height)

        text_density = image.text_density

        if text_density > max_text_density:
            deny_list.append(
                f"Изображение с подписью '{image.caption}' имеет слишком высокую плотность текста: "
                f"{text_density:.2f} (максимум {max_text_density:.2f}). "
                "Это может означать, что текст нечитаем.<br>"
            )

        if image.symbols_percentage is None:
            text_length = len(text)
            image.symbols_percentage = (
                count_symbols_in_text(text, symbols_set) / text_length * 100 if text_length else 0.0
            )

        symbols_percentage = image.symbols_percentage

        if symbols_percentage > max_symbols_percentage:
            deny_list.append(
                f"На изображении с подписью '{image.caption}' содержится слишком много "
                f"неверно распознанных символов: {symbols_percentage:.2f}% "
                f"(максимум {max_symbols_percentage:.2f}%). "
                "Это может означать, что размер шрифта слишком маленький "
                "или текст нечитаем.<br>"
            )

        image_methods.update_image(image)

    if deny_list:
        result = [[f'Проблемы с текстом на изображениях! <br>{"".join(deny_list)}'], 0]
    else:
        result = [['Текст на изображениях корректен!'], 1]

    add_tesseract_result(check_id, result)


def add_tesseract_result(check_id, result):
    updated_check = check_methods.get_check(ObjectId(check_id))
    celery_tesseract_methods.mark_celery_tesseract_task_as_finished_by_check(check_id, result)
    if celery_check_methods.get_celery_task_status_by_check(ObjectId(check_id)):
        update_tesseract_criteria_result(updated_check)
    check_methods.update_check(updated_check)


def update_tesseract_criteria_result(check):
    tesseract_task = celery_tesseract_methods.get_celery_tesseract_task_by_check(str(check._id))
    for criteria in check.enabled_checks:
        if criteria["id"] == 'image_text_check':
            criteria["verdict"] = tesseract_task['tesseract_result'][0]
            criteria["score"] = tesseract_task['tesseract_result'][1]
            check.score = max(
                0, round(check.score - (1 - tesseract_task['tesseract_result'][1]) / len(BASE_REPORT_CRITERION), 3)
            )
            check.is_ended = True
            return


def count_symbols_in_text(text, symbols_set):
    return sum(1 for char in text if char in symbols_set)


def calculate_text_density(text, image_area):
    text_without_spaces = ''.join(text.split())
    if image_area == 0:
        return 0
    return len(text_without_spaces) / image_area
