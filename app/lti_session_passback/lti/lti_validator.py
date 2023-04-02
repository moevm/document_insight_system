from db.db_methods import ConsumersDBManager
from oauthlib.oauth1 import RequestValidator


class LTIRequestValidator(RequestValidator):
    """
    https://github.com/oauthlib/oauthlib/blob/master/oauthlib/oauth1/rfc5849/request_validator.py
    """

    @property
    def client_key_length(self):
        return 15, 30

    @property
    def nonce_length(self):
        return 20, 40  # len(nonce_from_moodle) = 32. default_return = (20, 30)

    @property
    def enforce_ssl(self):
        return False

    @property
    def dummy_client(self):
        return 'dummy_client'

    def get_client_secret(self, client_key, request):
        return ConsumersDBManager.get_secret(client_key)

    def validate_client_key(self, client_key, request):
        return ConsumersDBManager.is_key_valid(client_key)

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None,
                                     access_token=None):
        if not ConsumersDBManager.has_timestamp_and_nonce(client_key, timestamp, nonce):
            ConsumersDBManager.add_timestamp_and_nonce(client_key, timestamp, nonce)
            return True
        else:
            return False
