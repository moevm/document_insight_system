import unittest
from unittest.mock import MagicMock
from app.main.checks.report_checks import ReportImageShareCheck
from tests_all.tests_check.base_test import BaseTestCase

class TestReportImageShareCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.mock_file.page_counter = MagicMock(return_value=5)
        self.mock_file.page_count = 5
        self.file_info['file'] = self.mock_file
        self.checker = ReportImageShareCheck(file_info=self.file_info, limit=0.3)

    def test_check_not_enough_pages(self):
        self.mock_file.page_counter.return_value = 3
        self.file_info['file'] = self.mock_file
        self.checker = ReportImageShareCheck(file_info=self.file_info, limit=0.3)
        result = self.checker.check()
        expected_output = "В отчете недостаточно страниц. Нечего проверять."
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_images_share_exceeds_limit(self):
        self.mock_file.pdf_file.page_images.return_value = 1000
        self.mock_file.pdf_file.page_height.return_value = 2000
        self.file_info['file'] = self.mock_file
        self.checker = ReportImageShareCheck(file_info=self.file_info, limit=0.3)
        result = self.checker.check()
        expected_output = (
            'Проверка не пройдена! Изображения в работе занимают около 0.5 объема '
            'документа без учета приложения, ограничение - 0.3'
            '''
                        Если доля отчета, приходящаяся на изображения, больше нормы, попробуйте сделать следующее:
                        <ul>
                            <li>Попробуйте перенести малозначимые иллюстрации в Приложение;</li>
                            <li>Если у вас уже есть раздел Приложение, убедитесь, что количество страниц в отчете посчитано программой без учета приложения;</li>
                            <li>Если страницы посчитаны программой неверно, убедитесь, что заголовок приложения правильно оформлен;</li>
                            <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
                        </ul>
                        '''
        )
        self.assertFalse(result['score'])
        self.assertIn(expected_output[:100], result['verdict'][0])

    def test_images_share_within_limit(self):
        self.mock_file.pdf_file.page_images.return_value = 500
        self.mock_file.pdf_file.page_height.return_value = 2000
        self.file_info['file'] = self.mock_file
        self.checker = ReportImageShareCheck(file_info=self.file_info, limit=0.3)
        result = self.checker.check()
        expected_output = 'Пройдена!'
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)


if __name__ == '__main__':
    unittest.main()
