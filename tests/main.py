import unittest
import sys
import argparse
from basic_selenium_test import BasicSeleniumTest
from test_statistic import StatisticTestSelenium
from test_authorization import AuthTestSelenium
from test_pres_load import PresLoadTestSelenium

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Selenium tests with specified host, login, and password.')
    parser.add_argument('--host', type=str, default='http://127.0.0.1:8080', help='Host address for testing')
    parser.add_argument('--login', type=str, required=True, help='insert Username')
    parser.add_argument('--password', type=str, required=True, help='insert Password')
    parser.add_argument('--pres', type=str, required=True, help='your path to press for testing')
    return parser.parse_args()

def main():
    args = parse_arguments()

    suite = unittest.TestSuite()
    suite.addTest(BasicSeleniumTest.parametrize(AuthTestSelenium, param=(args.host, args.login, args.password)))
    suite.addTest(BasicSeleniumTest.parametrize(StatisticTestSelenium, param=(args.host, args.login, args.password)))
    suite.addTest(BasicSeleniumTest.parametrize(PresLoadTestSelenium, param=(args.host, args.login, args.password, args.pres)))    

    returnCode = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    BasicSeleniumTest.closeDriver()
    sys.exit(returnCode)

if __name__ == '__main__':
    main()
