import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks import ReportFirstPagesCheck
from tests_all.tests_check.base_test import BaseTestCase

class TestReportFirstPagesCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.mock_file.page_counter.return_value = 10
        self.mock_file.make_headers = MagicMock(return_value=[])
        self.file_info['file'] = self.mock_file
        self.checker = ReportFirstPagesCheck(file_info=self.file_info)

    def test_all_required_pages_present(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Титульный лист", "marker": True},
            {"name": "Задание на выпускную квалификационную работу", "marker": True},
            {"name": "Календарный план", "marker": True},
            {"name": "Реферат", "marker": True},
            {"name": "Abstract", "marker": True},
            {"name": "Содержание", "marker": True},
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportFirstPagesCheck(file_info=self.file_info)
        result = self.checker.check()
        expected_output = "Все обязательные страницы найдены и их заголовки находятся на первой строке новой страницы."
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_some_required_pages_missing(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Титульный лист", "marker": True},
            {"name": "Задание на выпускную квалификационную работу", "marker": False},
            {"name": "Календарный план", "marker": True},
            {"name": "Реферат", "marker": False},
            {"name": "Abstract", "marker": True},
            {"name": "Содержание", "marker": True},
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportFirstPagesCheck(file_info=self.file_info)
        result = self.checker.check()
        expected_output = (
            'Следующие страницы не найдены либо их заголовки расположены не на первой строке новой '
            'страницы: <ul><li>Задание на выпускную квалификационную работу</li><li>Реферат</li></ul> '
            'Проверьте очередность листов и орфографию заголовков.'
        )
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_no_required_pages_present(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Титульный лист", "marker": False},
            {"name": "Задание на выпускную квалификационную работу", "marker": False},
            {"name": "Календарный план", "marker": False},
            {"name": "Реферат", "marker": False},
            {"name": "Abstract", "marker": False},
            {"name": "Содержание", "marker": False},
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportFirstPagesCheck(file_info=self.file_info)
        result = self.checker.check()
        expected_output = (
            'Следующие страницы не найдены либо их заголовки расположены не на первой строке новой '
            'страницы: <ul><li>Титульный лист</li><li>Задание на выпускную квалификационную работу</li>'
            '<li>Календарный план</li><li>Реферат</li><li>Abstract</li><li>Содержание</li></ul> '
            'Проверьте очередность листов и орфографию заголовков.'
        )
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

if __name__ == '__main__':
    unittest.main()