import configparser
import json
import os

from lti_session_passback.lti.utils import parse_consumer_info

# read ini file
current_ph = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(current_ph, 'config.ini')
config = configparser.ConfigParser()
config.read(ini_file)

# read version file
project_ph = os.path.dirname(current_ph)
version_file = os.path.join(project_ph, "app", "VERSION.json")
try:
    with open(version_file) as vfp:
        json_string = vfp.read()
        VERSION_DATA = json.loads(json_string)
except json.decoder.JSONDecodeError as error:
    VERSION_DATA = {
        "error": str(error),
        "data": error.doc
    }
except IOError as error:
    VERSION_DATA = {"error": f"{error.strerror}: {error.filename}"}
except Exception as error:
    VERSION_DATA = {"error": repr(error)}

# setup variables
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')

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
