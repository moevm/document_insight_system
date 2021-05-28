from os import environ

RECAPTCHA_SITE_KEY = environ.get('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = environ.get('RECAPTCHA_SECRET_KEY', '')
SECRET_KEY = environ.get('SECRET_KEY', '')
RECAPTCHA_ENABLED = True
