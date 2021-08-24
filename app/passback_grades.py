import sys
from time import sleep
from lti.tool_provider import ToolProvider
from app.bd_helper.bd_helper import ConsumersDBManager, get_unpassed_checks, set_passbacked_flag, get_user
from app.utils.repeated_timer import RepeatedTimer
from logging import getLogger
import configparser

config = configparser.ConfigParser()
config.read('app/config.ini')
logger = getLogger('root')

class ChecksPassBack:
    def __init__(self, timeout_seconds=10):
        self._timeout_seconds = timeout_seconds

    def grade_passback(self, check):
        user = check.get('user')
        passback_params = get_user(user).params_for_passback
        if not passback_params:
            return

        consumer_secret = ConsumersDBManager.get_secret(passback_params['oauth_consumer_key'])
        response = ToolProvider.from_unpacked_request(secret=consumer_secret, params=passback_params, headers=None, url=None).post_replace_result(score=check.get('score'))

        if response.code_major == 'success' and response.severity == 'status':
            logger.info('Score was successfully passed back: score = {}, check_id = {}'.format(check.get('score'), check.get('_id')))
            set_passbacked_flag(check.get('_id'), True)
        else:
            logger.warning('Passback failed for check_id = {}'.format(check.get('_id')))

    def _run(self):
        for check in get_unpassed_checks():
            self.grade_passback(check)

    def run(self):
        RepeatedTimer(self._timeout_seconds, self._run)

if __name__ == "__main__":
    passback_checks = ChecksPassBack(config.getint('consts', 'PASSBACK_TIMER'))
    passback_checks.run()
