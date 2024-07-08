import os
import unittest
import sys
import argparse
from basic_selenium_test import BasicSeleniumTest
from test_statistic import StatisticTestSelenium
from test_authorization import AuthTestSelenium
from test_single_card_check import SingleCheckTestSelenium
from test_version import VersionTestSelenium
from test_file_load import FileLoadTestSelenium

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Selenium tests with specified data')
    parser.add_argument('--host', type=str, default='http://127.0.0.1:8080', help='Host address for testing')
    parser.add_argument('--login', type=str, required=True, help='insert Username')
    parser.add_argument('--password', type=str, required=True, help='insert Password')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument('--pres', type=str, default=os.path.join(script_dir, 'tests_data/example_of_pres.pptx'), help='your path to press for testing')
    parser.add_argument('--report', type=str, default=os.path.join(script_dir, 'tests_data/example_of_report.docx'), help='your path to report in .docx')
    parser.add_argument('--report_doc', type=str, default=os.path.join(script_dir, 'tests_data/example_of_report.doc'), help='your path to report in .doc')
    
  
    return parser.parse_args()

def main():
    args = parse_arguments()

    suite = unittest.TestSuite()
    tests = (AuthTestSelenium, StatisticTestSelenium, FileLoadTestSelenium, SingleCheckTestSelenium, VersionTestSelenium)
    param = (args.host, args.login, args.password, args.report, args.report_doc, args.pres)
    for test in tests:
        suite.addTest(BasicSeleniumTest.parametrize(test, param=param))

    returncode = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    BasicSeleniumTest.close_driver()
    sys.exit(returncode)

if __name__ == '__main__':
    main()
