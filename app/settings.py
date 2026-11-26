import configparser
import os

from lti_session_passback.lti.utils import parse_consumer_info

from app.build_info import get_build_info

# read ini file
current_ph = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(current_ph, 'config.ini')
config = configparser.ConfigParser()
config.read(ini_file)

BUILD_INFO = get_build_info()

# setup variables
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')


SECRET_KEY = os.environ.get('SECRET_KEY', '')
SIGNUP_PAGE_ENABLED = os.environ.get('SIGNUP_PAGE_ENABLED', 'True') == 'True'

MAX_CONTENT_LENGTH = config.getint('consts', 'MAX_CONTENT_LENGTH') * 1024 * 1024
MAX_SYSTEM_STORAGE = config.getint('consts', 'MAX_SYSTEM_STORAGE') * 1024 * 1024

DEBUG_AUTH = False
consumer_keys = os.environ.get('CONSUMER_KEY', '')
consumer_secrets = os.environ.get('CONSUMER_SECRET', '')
if consumer_keys == '' or consumer_secrets == '':
    raise Exception('Required CONSUMER_KEY or CONSUMER_SECRET missing')
LTI_CONSUMERS = parse_consumer_info(consumer_keys, consumer_secrets)
