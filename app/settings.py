import configparser
import os
import json

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
        try:
            VERSION_DATA = json.loads(json_string)
        except Exception as error:
            VERSION_DATA = {
                "error": str(error),
                "data": json_string
            }            
except Exception as error:
    VERSION_DATA = { "error": str(error) }

# setup variables
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')

SECRET_KEY = os.environ.get('SECRET_KEY', '')

MAX_CONTENT_LENGTH = config.getint('consts', 'MAX_CONTENT_LENGTH')*1024*1024
MAX_SYSTEM_STORAGE = config.getint('consts', 'MAX_SYSTEM_STORAGE')*1024*1024
