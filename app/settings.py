from os import environ

ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD', '')

RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = environ.get('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = environ.get('RECAPTCHA_SECRET_KEY', '')

SECRET_KEY = environ.get('SECRET_KEY', '')

