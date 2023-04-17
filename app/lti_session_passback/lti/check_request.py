from db.db_methods import ConsumersDBManager
from lti.contrib.flask import FlaskToolProvider
from utils.mock_lti_auth import mock_lti_auth

from .lti_validator import LTIRequestValidator


def check_request(request):
    if not mock_lti_auth():
        return _check_request(request)
    else:
        return _mock_check_request(request)


def _check_request(request):
    provider = FlaskToolProvider.from_flask_request(
        secret=ConsumersDBManager.get_secret(request.args.get('oauth_consumer_key', None)),
        request=request)
    return provider.is_valid_request(LTIRequestValidator())


def _mock_check_request(request):
    return True
