import configparser
import os

current_ph = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(current_ph, 'config.ini')
config = configparser.ConfigParser()
config.read(ini_file)

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')

SECRET_KEY = os.environ.get('SECRET_KEY', '')
SIGNUP_PAGE_ENABLED = (os.environ.get('SIGNUP_PAGE_ENABLED', 'True') == 'True')

MAX_CONTENT_LENGTH = config.getint('consts', 'MAX_CONTENT_LENGTH')*1024*1024
MAX_SYSTEM_STORAGE = config.getint('consts', 'MAX_SYSTEM_STORAGE')*1024*1024
