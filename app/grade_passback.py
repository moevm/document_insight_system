import sys
from time import sleep
from lti.contrib.flask import FlaskToolProvider
from app.bd_helper.bd_helper import ConsumersDBManager
from lti.outcome_request import OutcomeRequest, REPLACE_REQUEST
from app.utils.mock_lti_auth import mock_lti_auth

class CheckToPassBackProcessor:
    def __init__(self, timeout_seconds=10):
        self._timeout_seconds = timeout_seconds

    def grade_passback(self, checks_db, check_id, is_retry):
        #params_for_passback = checks('check_id').
        consumer_secret = ConsumersDBManager.get_secret(params_for_passback.get('oauth_consumer_key'))
        request = OutcomeRequest({
            "consumer_key": params_for_passback.oauth_consumer_key,
            "consumer_secret": consumer_secret,
            "lis_outcome_service_url": params_for_passback.lis_outcome_service_url, #?pass to consumer
            "lis_result_sourcedid": params_for_passback.lis_result_sourcedid,
        })
        #score = checks('check_id').score
        request.post_replace_result(score)
        if request.was_outcome_post_successful() or mock_lti_auth():
            #update is_passbacked in checks
        else:
            #update is_passbacked in checks
