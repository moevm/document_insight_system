import logging
import sys
from datetime import datetime

from check_log_context import current_check_id, current_check_stage
from db.db_methods import add_log


class MongoDBLoggingHandler(logging.StreamHandler):
    def __init__(self, service_name):
        super().__init__()
        self.setLevel(logging.DEBUG)
        self.service_name = service_name

    def emit(self, record):
        if not record.msg:
            return
        add_log(
            timestamp=datetime.now(),
            serviceName=self.service_name,
            levelname=record.levelname,
            levelno=record.levelno,
            message=self.format(record),
            pathname=record.pathname,
            filename=record.filename,
            funcName=record.funcName,
            lineno=record.lineno,
            check_id=current_check_id.get(),
            stage=current_check_stage.get(),
        )


def get_root_logger(service_name):
    root_logger = logging.getLogger('root_logger')
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)

    line_formatter = None
    for handler in logging.getLogger().handlers:
        if handler.formatter is not None:
            line_formatter = handler.formatter
            break
    if line_formatter is None:
        line_formatter = logging.Formatter()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(line_formatter)
    mongo_handler = MongoDBLoggingHandler(service_name)
    mongo_handler.setFormatter(line_formatter)
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(mongo_handler)
    root_logger.propagate = False
    return root_logger
