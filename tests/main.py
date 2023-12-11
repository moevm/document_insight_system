import unittest
import sys
from basic_selenium_test import BasicSeleniumTest
from test_authorization import AuthTestSelenium


def main(host):
    suite = unittest.TestSuite()

    suite.addTest(
        BasicSeleniumTest.parametrize(
            AuthTestSelenium,
            param=host))

    returnCode = not unittest.TextTestRunner(
        verbosity=2).run(suite).wasSuccessful()

    BasicSeleniumTest.closeDriver()
    sys.exit(returnCode)


if __name__ == '__main__':
    host_arg = 'https://slides-checker.moevm.info'
    main(host_arg)
