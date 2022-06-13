from .db_methods import client
import logging
logger = logging.getLogger('root_logger')

client.drop_database('pres-parser-db')
logger.info("Вся информация очищена!")
