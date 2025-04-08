import logging

from .db_methods import client

logger = logging.getLogger('root_logger')

client.drop_database('dis-db')
logger.info("Вся информация очищена!")
