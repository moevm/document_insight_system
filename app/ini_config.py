import configparser
import os

current_ph = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(current_ph, 'config.ini')
config = configparser.ConfigParser()
config.read(ini_file)

MAX_CONTENT_LENGTH = config.get('consts', 'MAX_CONTENT_LENGTH')
