from lti.contrib.flask import FlaskToolProvider
from .lti_validator import LTIRequestValidator
from app.bd_helper.bd_helper import ConsumersDBManager

def check_request(request):
    provider = FlaskToolProvider.from_flask_request(
              secret = ConsumersDBManager.get_secret(request.args.get('oauth_consumer_key', None)),
              request = request)
    return provider.is_valid_request(LTIRequestValidator())
