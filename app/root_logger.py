import logging
import sys
from datetime import datetime

from db.db_methods import add_log


class MongoDBLoggingHandler(logging.StreamHandler):
    def __init__(self, service_name):
        super().__init__()
        self.setLevel(logging.DEBUG)
        self.service_name = service_name

    def emit(self, record):
        if not record.msg:
            return
        add_log(timestamp=datetime.now(),
                serviceName=self.service_name,
                levelname=record.levelname,
                levelno=record.levelno,
                message=self.format(record),
                pathname=record.pathname,
                filename=record.filename,
                funcName=record.funcName,
                lineno=record.lineno)


def get_logging_stdout_handler():
    logging_stdout_handler = logging.StreamHandler(sys.stdout)
    logging_stdout_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
                                  '%y-%m-%d %H:%M:%S')
    logging_stdout_handler.setFormatter(formatter)
    return logging_stdout_handler


def get_root_logger(service_name):
    root_logger = logging.getLogger('root_logger')
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(get_logging_stdout_handler())
    root_logger.addHandler(MongoDBLoggingHandler(service_name))
    root_logger.propagate = False
    return root_logger
