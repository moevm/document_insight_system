import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks import ReportSectionComponent
from tests_all.tests_check.base_test import BaseTestCase

class TestReportSectionComponent(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.file_info['file'] = self.mock_file
        self.checker = ReportSectionComponent(file_info=self.file_info)

    def test_all_components_present(self):
        self.mock_file.page_counter.return_value = 5
        self.mock_file.make_chapters.return_value = [
            {"text": "Введение", "child": [
                {"text": "Цель работы - изучение."},
                {"text": "Задачи исследования."},
                {"text": "Объект исследования."},
                {"text": "Предмет исследования."}
            ]}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportSectionComponent(file_info=self.file_info)
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], 'Все необходимые компоненты раздела "Введение" обнаружены!')

    def test_some_components_missing(self):
        self.mock_file.page_counter.return_value = 5
        self.mock_file.make_chapters.return_value = [
            {"text": "Введение", "child": [
                {"text": "Цель работы - изучение."},
                {"text": "Задачи исследования."}
            ]}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportSectionComponent(file_info=self.file_info)
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('Не найдены следующие компоненты раздела Введение:', result['verdict'][0])
        self.assertIn('<li>Объект</li>', result['verdict'][0])
        self.assertIn('<li>Предмет</li>', result['verdict'][0])

    def test_no_introduction_section(self):
        self.mock_file.page_counter.return_value = 5
        self.mock_file.make_chapters.return_value = [
            {"text": "Методология", "child": [
                {"text": "Цель работы - изучение."},
                {"text": "Задачи исследования."}
            ]}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportSectionComponent(file_info=self.file_info)
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], 'Раздел "Введение" не обнаружен!')

    def test_insufficient_pages(self):
        self.mock_file.page_counter.return_value = 3
        self.file_info['file'] = self.mock_file
        self.checker = ReportSectionComponent(file_info=self.file_info)
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], "В отчете недостаточно страниц. Нечего проверять.")

if __name__ == '__main__':
    unittest.main()
