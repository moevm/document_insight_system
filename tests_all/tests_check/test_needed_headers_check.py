import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks import ReportNeededHeadersCheck
from tests_all.tests_check.base_test import BaseTestCase

class TestReportNeededHeadersCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.mock_file.page_counter.return_value = 5
        self.file_info['file'] = self.mock_file
        self.checker = ReportNeededHeadersCheck(file_info=self.file_info)

    def test_all_headers_present(self):
        self.mock_file.make_chapters.return_value = [
            {"text": "Введение", "style": "heading 2"},
            {"text": "Обзор литературы", "style": "heading 2"},
            {"text": "Методы исследования", "style": "heading 2"},
            {"text": "Заключение", "style": "heading 2"}
        ]
        self.mock_file.find_header_page.return_value = 1
        self.mock_file.show_chapters.return_value = "Иерархия заголовков"
        self.file_info['file'] = self.mock_file
        self.checker = ReportNeededHeadersCheck(file_info=self.file_info)
        self.checker.patterns = ["Введение", "Обзор литературы", "Методы исследования", "Заключение"]
        result = self.checker.check()
        expected_output = 'Все необходимые заголовки обнаружены!'
        self.assertTrue(result['score'])
        self.assertIn(expected_output, result['verdict'][0])

    def test_missing_headers(self):
        self.mock_file.make_chapters.return_value = [
            {"text": "Введение", "style": "heading 2"},
            {"text": "Методы исследования", "style": "heading 2"}
        ]
        self.mock_file.find_header_page.return_value = 1
        self.mock_file.show_chapters.return_value = "Иерархия заголовков"
        self.file_info['file'] = self.mock_file
        self.checker = ReportNeededHeadersCheck(file_info=self.file_info)
        self.checker.patterns = ["Введение", "Обзор литературы", "Методы исследования", "Заключение"]
        result = self.checker.check()
        expected_output = 'Не найдены следующие обязательные заголовки:'
        self.assertFalse(result['score'])
        self.assertIn(expected_output, result['verdict'][0])
        self.assertIn('<li>Обзор литературы</li>', result['verdict'][0])
        self.assertIn('<li>Заключение</li>', result['verdict'][0])

    def test_no_headers(self):
        self.mock_file.make_chapters.return_value = []
        self.mock_file.find_header_page.return_value = 1
        self.mock_file.show_chapters.return_value = "Иерархия заголовков"
        self.file_info['file'] = self.mock_file
        self.checker = ReportNeededHeadersCheck(file_info=self.file_info)
        result = self.checker.check()
        expected_output = "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей."
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_insufficient_pages(self):
        self.mock_file.page_counter.return_value = 3
        self.file_info['file'] = self.mock_file
        self.checker = ReportNeededHeadersCheck(file_info=self.file_info)
        result = self.checker.check()
        expected_output = "В отчете недостаточно страниц. Нечего проверять."
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)


if __name__ == '__main__':
    unittest.main()
