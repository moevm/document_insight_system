import os
from celery import Celery
from celery.signals import worker_ready
import pytesseract
import cv2
import numpy as np
from root_logger import get_root_logger

TASK_RETRY_COUNTDOWN = 60
MAX_RETRIES = 2

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

@celery.task(name="tesseract_recognize", queue='tesseract-queue', bind=True, max_retries=MAX_RETRIES)
def tesseract_recognize(self, image_id, image_data):
    try:
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        img_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img_cv is None:
            raise ValueError("Не удалось декодировать изображение из двоичных данных")
        text = pytesseract.image_to_string(img_cv, **TESSERACT_CONFIG)
        if text is None:
            logger.warning(f"Tesseract вернул None для image_id: {image_id}.")
            text = ""
        logger.info(f"Текст успешно распознан для image_id: {image_id}")
        return text

    except Exception as e:
        logger.error(f"Ошибка при распознавании текста: {e}", exc_info=True)
        logger.info(f"Пустая строка записана для image_id: {image_id} из-за ошибки: {e}")
        if self.request.retries >= self.max_retries:
            logger.error(f"Достигнуто максимальное количество попыток для image_id: {image_id}")
            return f"Ошибка: {e}"
        logger.info(f"Повторная попытка распознавания для image_id: {image_id}. Попытка {self.request.retries + 1} из {self.max_retries}.")
        self.retry(countdown=TASK_RETRY_COUNTDOWN)