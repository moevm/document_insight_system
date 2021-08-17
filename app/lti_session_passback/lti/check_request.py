from lti.contrib.flask import FlaskToolProvider
from .lti_validator import LTIRequestValidator
from app.utils.mock_lti_auth import mock_lti_auth
from app.bd_helper.bd_helper import ConsumersDBManager


def check_request(request):
    if not mock_lti_auth():
        return _check_request(request)
    else:
        return _mock_check_request(request)


def _check_request(request):
    provider = FlaskToolProvider.from_flask_request(request = request)
    return provider.is_valid_request(LTIRequestValidator())


def _mock_check_request(request):
    return True
