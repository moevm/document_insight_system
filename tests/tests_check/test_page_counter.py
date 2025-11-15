import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks import ReportPageCounter
from tests.tests_check.base_test import BaseTestCase

class TestReportPageCounter(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.mock_file.page_counter.return_value = 5
        self.file_info['file'] = self.mock_file
        self.checker = ReportPageCounter(file_info=self.file_info)

    def test_within_range(self):
        self.mock_file.page_counter.return_value = 100
        self.mock_file.page_count = 100
        self.file_info['file'] = self.mock_file
        self.checker = ReportPageCounter(file_info=self.file_info)
        result = self.checker.check()
        expected_output = "Пройдена! В отчете 100 стр не считая Приложения."
        self.assertTrue(result['score'])
        self.assertIn(expected_output, result['verdict'][0])

    def test_below_minimum(self):
        self.mock_file.page_counter.return_value = 40
        self.mock_file.page_count = 40
        self.file_info['file'] = self.mock_file
        self.checker = ReportPageCounter(file_info=self.file_info)
        result = self.checker.check()
        expected_output = 'Неверное количество страниц в файле: должно быть [50, 150] стр.'
        self.assertFalse(result['score'])
        self.assertIn(expected_output, result['verdict'][0])

    def test_above_maximum(self):
        self.mock_file.page_counter.return_value = 160
        self.mock_file.page_count = 160
        self.file_info['file'] = self.mock_file
        self.checker = ReportPageCounter(file_info=self.file_info)
        result = self.checker.check()
        expected_output = 'Неверное количество страниц в файле: должно быть [50, 150] стр.'
        self.assertFalse(result['score'])
        self.assertIn(expected_output, result['verdict'][0])

    def test_with_no_max_limit(self):
        self.mock_file.page_counter.return_value = 160
        self.mock_file.page_count = 160
        self.file_info['file'] = self.mock_file
        self.checker = ReportPageCounter(file_info=self.file_info, min_number=50, max_number=None)
        result = self.checker.check()
        expected_output = "Пройдена! В отчете 160 стр не считая Приложения."
        self.assertTrue(result['score'])
        self.assertIn(expected_output, result['verdict'][0])

if __name__ == '__main__':
    unittest.main()
