import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks import ReportRightWordsCheck
from tests.tests_check.base_test import BaseTestCase

class TestReportRightWordsCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.mock_file.page_counter.return_value = 5
        self.file_info['file'] = self.mock_file
        self.checker = ReportRightWordsCheck(file_info=self.file_info)

    def test_right_words_present(self):
        self.mock_file.page_counter.return_value = 5
        self.mock_file.pdf_file.get_text_on_page.return_value = {
            1: "Введение. Цель работы - изучение.",
            2: "Методология. В работе используются методы.",
            3: "Результаты. Исследования показали.",
            4: "Обсуждение. Выводы и рекомендации.",
            5: "Заключение. Цель достигнута."
        }
        self.file_info['file'] = self.mock_file
        self.checker = ReportRightWordsCheck(file_info=self.file_info)
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], "Пройдена!")

    def test_right_words_absent(self):
        self.mock_file.page_counter.return_value = 5
        self.mock_file.pdf_file.get_text_on_page.return_value = {
            1: "Введение. Задачи исследования.",
            2: "Методология. В работе используются методы.",
            3: "Результаты. Исследования показали.",
            4: "Обсуждение. Выводы и рекомендации.",
            5: "Заключение. Задачи выполнены."
        }
        self.file_info['file'] = self.mock_file
        self.checker = ReportRightWordsCheck(file_info=self.file_info)
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('Не найдены слова, соответствующие следующим регулярным выражениям: <ul><li>цел[ьией]</ul>', result['verdict'])

    def test_insufficient_pages(self):
        self.mock_file.page_counter.return_value = 3
        self.file_info['file'] = self.mock_file
        self.checker = ReportRightWordsCheck(file_info=self.file_info)
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], "В отчете недостаточно страниц. Нечего проверять.")

    def test_case_insensitivity(self):
        self.mock_file.page_counter.return_value = 5
        self.mock_file.pdf_file.get_text_on_page.return_value = {
            1: "Введение. ЦЕЛЬ работы - изучение.",
            2: "Методология. В работе используются методы.",
            3: "Результаты. Исследования показали.",
            4: "Обсуждение. Выводы и рекомендации.",
            5: "Заключение. цель достигнута."
        }
        self.file_info['file'] = self.mock_file
        self.checker = ReportRightWordsCheck(file_info=self.file_info)
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], "Пройдена!")

if __name__ == '__main__':
    unittest.main()
