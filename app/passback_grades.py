import configparser

import urllib3

from db.db_methods import ConsumersDBManager, get_unpassed_checks, set_passbacked_flag
from lti_session_passback.lti_provider import LTIProvider
from root_logger import get_root_logger
from utils import RepeatedTimer

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
config = configparser.ConfigParser()
config.read('app/config.ini')

logger = get_root_logger('passback_grades')


def check_success_response(response):
    return response.code_major == 'success' and response.severity == 'status'


class ChecksPassBack:
    def __init__(self, timeout_seconds=10):
        self._timeout_seconds = timeout_seconds

    def grade_passback(self, check):
        passback_params = check.get('params_for_passback', None)
        if not passback_params or passback_params["lis_outcome_service_url"] == "lis_outcome_service_url":
            set_passbacked_flag(check.get('_id'), None)
            return

        consumer_secret = ConsumersDBManager.get_secret(passback_params['oauth_consumer_key'])
        provider = LTIProvider.from_unpacked_request(secret=consumer_secret, params=passback_params, headers=None,
                                                     url=None)

        current_lms_result = provider.post_read_result()
        current_lms_score = float(current_lms_result.score) if check_success_response(current_lms_result) else 0.0
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

    def _run(self):
        logger.info('Start passback')
        for check in get_unpassed_checks():
            try:
                self.grade_passback(check)
            except Exception as exc:
                logger.error(str(exc))

    def run(self):
        RepeatedTimer(self._timeout_seconds, self._run)


if __name__ == "__main__":
    passback_checks = ChecksPassBack(config.getint('consts', 'PASSBACK_TIMER'))
    passback_checks.run()
