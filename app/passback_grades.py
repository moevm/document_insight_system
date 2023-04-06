import configparser

import urllib3

from db.db_methods import ConsumersDBManager, get_unpassed_checks, set_passbacked_flag
from lti_session_passback.lti_provider import LTIProvider
from root_logger import get_root_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
config = configparser.ConfigParser()
config.read('app/config.ini')

logger = get_root_logger('passback_grades')


def check_success_response(response):
    return response.code_major == 'success' and response.severity == 'status'


def grade_passback(check):
    passback_params = check.get('params_for_passback', None)
    if not passback_params or passback_params["lis_outcome_service_url"] == "lis_outcome_service_url":
        set_passbacked_flag(check.get('_id'), None)
        return

    consumer_secret = ConsumersDBManager.get_secret(passback_params['oauth_consumer_key'])
    provider = LTIProvider.from_unpacked_request(secret=consumer_secret, params=passback_params, headers=None,
                                                 url=None)

    #current_lms_result = provider.post_read_result()
    current_lms_score = -1 #float(current_lms_result.score) if check_success_response(current_lms_result) else 0.0
    system_score = check.get('score')

    if round(system_score, 2) > current_lms_score:
        # if our score > lms_score -> send, else - ???
        response = provider.post_replace_result(score=check.get('score'))

        if check_success_response(response):
            logger.info('Score was successfully passed back: score = {}, check_id = {}'.format(check.get('score'),
                                                                                               check.get('_id')))
            set_passbacked_flag(check.get('_id'), True)
        else:
            logger.error('Passback failed for check_id = {}'.format(check.get('_id')))
    else:
        logger.info(
            'LMS score is more then current (not passbacked): LMS_score = {}, system_score = {} check_id = {}'.format(
                current_lms_score, check.get('score'), check.get('_id')))
        set_passbacked_flag(check.get('_id'), None)


def run_passback():
    errors, passbacked = [], []
    for check in get_unpassed_checks():
        try:
            grade_passback(check)
            passbacked.append(str(check['_id']))
        except Exception as exc:
            logger.error(str(exc))
            errors.append(str(check['_id']))
    result = {'passbacked': passbacked, 'errors': errors}
    if passbacked or errors: logger.debug(str(result))
    return result
