import logging

from .db_main import client

logger = logging.getLogger('root_logger')


def drop_database():
    client.drop_database('pres-parser-db')
