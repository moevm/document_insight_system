from app.bd_helper.bd_helper import *
import logging
logger = logging.getLogger('root_logger')

client.drop_database('pres-parser-db')
logger.info("Вся информация очищена!")
