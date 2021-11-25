from app.bd_helper.bd_helper import *
from app.root_logger import get_root_logger
logger = get_root_logger('clear_users')

client.drop_database('pres-parser-db')
logger.info("Вся информация очищена!")
