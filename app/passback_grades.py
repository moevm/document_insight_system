import configparser


from db.db_methods import ConsumersDBManager, get_unpassed_checks, set_passbacked_flag, get_user
from root_logger import get_root_logger
from utils import RepeatedTimer
from lti_session_passback.lti_provider import LTIProvider

config = configparser.ConfigParser()
config.read('app/config.ini')

logger = get_root_logger('passback_grades')


class ChecksPassBack:
    def __init__(self, timeout_seconds=10):
        self._timeout_seconds = timeout_seconds

    def grade_passback(self, check):
        user = check.get('user')
        passback_params = get_user(user).params_for_passback
        if not passback_params or passback_params["lis_outcome_service_url"] == "lis_outcome_service_url":
            set_passbacked_flag(check.get('_id'), None)
            return

        consumer_secret = ConsumersDBManager.get_secret(passback_params['oauth_consumer_key'])
        response = LTIProvider.from_unpacked_request(secret=consumer_secret, params=passback_params, headers=None,
                                                      url=None).post_replace_result(score=check.get('score'))

        if response.code_major == 'success' and response.severity == 'status':
            logger.info('Score was successfully passed back: score = {}, check_id = {}'.format(check.get('score'),
                                                                                               check.get('_id')))
            set_passbacked_flag(check.get('_id'), True)
        else:
            logger.error('Passback failed for check_id = {}'.format(check.get('_id')))

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
