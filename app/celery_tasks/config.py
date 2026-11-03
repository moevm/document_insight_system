import os
from configparser import ConfigParser
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent

FILES_FOLDER = '/usr/src/project/files'

config = ConfigParser()
config.read(APP_DIR / "config.ini")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")
CELERY_TIMEZONE = "Europe/Moscow"

CELERY_BEAT_SCHEDULE = {
    "passback-grades": {
        "task": "passback-task",
        "schedule": config.getint("consts", "PASSBACK_TIMER"),
    },
}

CHECK_TASK_RETRY_COUNTDOWN = 60
CHECK_MAX_TASK_RETRIES = 3

TESSERACT_TASK_RETRY_COUNTDOWN = 30
TESSERACT_MAX_RETRIES = 1
TESSERACT_TASK_SOFT_TIME_LIMIT = 120
TESSERACT_CALLBACK_SOFT_TIME_LIMIT = 30
TESSERACT_CONFIG = {
    "lang": "rus+eng",
    "config": "--psm 6",
}
