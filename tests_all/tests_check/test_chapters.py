import unittest
from unittest.mock import MagicMock
from tests_all.tests_check.base_test import BaseTestCase
from app.main.checks.base_check import morph, answer
from app.main.checks.report_checks import ReportChapters

class TestReportChaptersCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.file_info['file'].page_counter.return_value = 5
        self.check = ReportChapters(file_info=self.file_info)

    def test_check_not_enough_pages(self):
        self.file_info['file'].page_counter.return_value = 3  # Недостаточное количество страниц
        result = self.check.check()
        self.assertEqual(result, answer(False, "В отчете недостаточно страниц. Нечего проверять."))

    def test_check_no_headers_found(self):
        self.file_info['file'].make_chapters.return_value = []  # Пустой список заголовков
        result = self.check.check()
        self.assertEqual(result, answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей."))

    def test_check_valid_headers(self):
        # Подготовка заголовков
        mock_headers = [
            {"text": "Заголовок 1", "style": "Заголовок", "styled_text": {"runs": [{"text": "Заголовок 1", "style": MagicMock()}]}},
            {"text": "Заголовок 2", "style": "Заголовок", "styled_text": {"runs": [{"text": "Заголовок 2", "style": MagicMock()}]}}
        ]
        self.file_info['file'].make_chapters.return_value = mock_headers

        # Настройка
        self.check.docx_styles = {
            0: ["Заголовок"]
        }
        self.check.target_styles = {
            0: {"style": MagicMock()}
        }
        self.check.style_regex = {
            0: MagicMock()
        }

        result = self.check.check()
        self.assertEqual(result['score'], 1)
        self.assertTrue("Форматирование заголовков соответствует требованиям." in result['verdict'])

    def test_check_invalid_headers(self):
        # Подготовка заголовков с несоответствующим стилем
        mock_headers = [
            {"text": "Заголовок 1", "style": "Неверный стиль", "styled_text": {"runs": [{"text": "Заголовок 1", "style": MagicMock()}]}},
            {"text": "Заголовок 2", "style": "Неверный стиль", "styled_text": {"runs": [{"text": "Заголовок 2", "style": MagicMock()}]}}
        ]
        self.file_info['file'].make_chapters.return_value = mock_headers

        # Настройка
        self.check.docx_styles = {
            0: ["Заголовок"]
        }
        self.check.target_styles = {
            0: {"style": MagicMock()}
        }
        self.check.style_regex = {
            0: MagicMock()
        }

        result = self.check.check()
        self.assertEqual(result['score'], 0)
        self.assertFalse("Найдены ошибки в оформлении заголовков" in result['verdict'])

if __name__ == '__main__':
    unittest.main()
