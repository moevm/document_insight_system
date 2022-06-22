from distutils.util import strtobool

from settings import DEBUG_AUTH


def safe_strtobool(value, on_error=False):
    if isinstance(value, bool):
        return value
    try:
        return bool(strtobool(value))
    except ValueError:
        return on_error


def mock_lti_auth():
    try:
        return safe_strtobool(DEBUG_AUTH)
    except Exception:
        return False
