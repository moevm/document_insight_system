import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks.simple_check import ReportSimpleCheck
from tests.tests_check.base_test import BaseTestCase

class TestReportSimpleCheck(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.file_info['file'] = self.mock_file

    def test_file_not_empty(self):
        self.mock_file.paragraphs = ["Это текст параграфа."]
        self.file_info['file'] = self.mock_file
        checker = ReportSimpleCheck(file_info=self.file_info)
        result = checker.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], "Пройдена!")

    def test_file_empty(self):
        self.mock_file.paragraphs = []
        self.file_info['file'] = self.mock_file
        checker = ReportSimpleCheck(file_info=self.file_info)
        result = checker.check()
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], 'В файле нет текста.')

if __name__ == '__main__':
    unittest.main()
