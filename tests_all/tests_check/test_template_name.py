import unittest
from unittest.mock import MagicMock
from datetime import datetime
from app.main.checks.report_checks.template_name import ReportTemplateNameCheck
from app.main.checks.base_check import answer
from tests_all.tests_check.base_test import BaseTestCase

class TestReportTemplateNameCheck(BaseTestCase):

    def setUp(self):
        self.mock_file_info = {
            'file': MagicMock(),
            'filename': f'{datetime.now().year}ВКР111111ИВАНОВ.pdf'
        }
        self.checker = ReportTemplateNameCheck(file_info=self.mock_file_info)

    def test_correct_filename(self):
        self.mock_file_info['filename'] = f'{datetime.now().year}ВКР111111ИВАНОВ.pdf'
        self.checker.filename = self.mock_file_info['filename'].split('.', 1)[0]
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], "Пройдена!")

    def test_incorrect_filename(self):
        self.mock_file_info['filename'] = f'{datetime.now().year}ВКР111111ivanov.pdf'
        self.checker.filename = self.mock_file_info['filename'].split('.', 1)[0]
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('не соответствует шаблону', result['verdict'][0])

    def test_missing_year(self):
        self.mock_file_info['filename'] = 'ВКР111111ИВАНОВ.pdf'
        self.checker.filename = self.mock_file_info['filename'].split('.', 1)[0]
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('не соответствует шаблону', result['verdict'][0])

    def test_missing_vkr(self):
        self.mock_file_info['filename'] = f'{datetime.now().year}111111ИВАНОВ.pdf'
        self.checker.filename = self.mock_file_info['filename'].split('.', 1)[0]
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('не соответствует шаблону', result['verdict'][0])

    def test_short_student_id(self):
        self.mock_file_info['filename'] = f'{datetime.now().year}ВКР11111ИВАНОВ.pdf'
        self.checker.filename = self.mock_file_info['filename'].split('.', 1)[0]
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('не соответствует шаблону', result['verdict'][0])

    def test_non_cyrillic_surname(self):
        self.mock_file_info['filename'] = f'{datetime.now().year}ВКР111111IVANOV.pdf'
        self.checker.filename = self.mock_file_info['filename'].split('.', 1)[0]
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertIn('не соответствует шаблону', result['verdict'][0])

if __name__ == '__main__':
    unittest.main()
