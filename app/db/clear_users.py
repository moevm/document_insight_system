import logging

from .db_main import client

logger = logging.getLogger('root_logger')

client.drop_database('pres-parser-db')
logger.info("Вся информация очищена!")
