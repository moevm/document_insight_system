import unittest
from unittest.mock import Mock
from datetime import datetime
# from utils import format_header
from app.main.checks.presentation_checks.sld_enum import SldEnumCheck

class TestSldEnumCheck(unittest.TestCase):

    def setUp(self):
        self.file_info = {
            'file': Mock(),
            'filename': f'{datetime.now().year}ВКР111111ИВАНОВ.pdf',
            'pdf_id': '12345'
        }
        self.file_info['file'].slides = [
            Mock(page_number=[-1]),
            Mock(page_number=[2]),
            Mock(page_number=[3]),
            Mock(page_number=[4]),
            Mock(page_number=[5])
        ]

    def test_correct_slide_numbering(self):
        checker = SldEnumCheck(self.file_info)

        result = checker.check()

        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], "Пройдена!")

    def test_incorrect_slide_numbering(self):
        self.file_info['file'].slides[1].page_number = [3]

        checker = SldEnumCheck(self.file_info)

        result = checker.check()

        self.assertFalse(result['score'])
        self.assertIn("Не пройдена", result['verdict'][0])

    def test_multiple_errors(self):
        self.file_info['file'].slides[1].page_number = [3]
        self.file_info['file'].slides[3].page_number = [5]

        checker = SldEnumCheck(self.file_info)
        result = checker.check()

        self.assertFalse(result['score'])
        self.assertIn("Не пройдена", result['verdict'][0])
        self.assertIn('проблемные слайды: ', result['verdict'][0])

if __name__ == '__main__':
    unittest.main()

