from app.bd_helper.bd_helper import *
from logging import getLogger
logger = getLogger('root')

client.drop_database('pres-parser-db')
logger.info("Вся информация очищена!")
