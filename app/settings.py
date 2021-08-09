import configparser
from json.decoder import JSONDecodeError
import os
import json
from tempfile import mkdtemp

# read ini file
current_ph = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(current_ph, 'config.ini')
config = configparser.ConfigParser()
config.read(ini_file)

# read version file
version_ph = os.path.dirname(current_ph)
version_file = os.path.join(version_ph, "VERSION.json")
try:
    with open(version_file) as vfp:
        json_string = vfp.read()
        VERSION_DATA = json.loads(json_string)
except JSONDecodeError as error:
    VERSION_DATA = {
        "error": str(error),
        "data": error.doc
    }
except IOError as error:
    VERSION_DATA = {"error": f"{error.strerror}: {error.filename}"}
except Exception as error:
    VERSION_DATA = { "error": repr(error) }

# setup variables
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')

SECRET_KEY = os.environ.get('SECRET_KEY', '')
SIGNUP_PAGE_ENABLED = os.environ.get('SIGNUP_PAGE_ENABLED', 'True') == 'True'

MAX_CONTENT_LENGTH = config.getint('consts', 'MAX_CONTENT_LENGTH')*1024*1024
MAX_SYSTEM_STORAGE = config.getint('consts', 'MAX_SYSTEM_STORAGE')*1024*1024

CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 600
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = mkdtemp()

SESSION_COOKIE_NAME = 'flask-session-id'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False   # should be True in case of HTTPS usage (production)
SESSION_COOKIE_SAMESITE = None  # should be 'None' in case of HTTPS usage (production)
