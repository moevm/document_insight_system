import unittest
from unittest.mock import Mock, MagicMock

from app.main.checks.base_check import morph, answer
from app.main.checks.presentation_checks.image_share import PresImageShareCheck


class TestPresImageShareCheck(unittest.TestCase):

    def setUp(self):
        slide_with_image = Mock()
        slide_with_image.get_images.return_value = ['image1']
        slide_with_image.get_page_number.return_value = 1

        slide_without_image = Mock()
        slide_without_image.get_images.return_value = []
        slide_without_image.get_page_number.return_value = 2

        self.mock_file_info = {
            'file': Mock(),
            'filename': 'presentation.pptx',
            'pdf_id': '123'
        }
        self.mock_file_info['file'].slides = [slide_with_image, slide_without_image, slide_with_image]
        self.checker = PresImageShareCheck(self.mock_file_info)

    def test_images_below_limit(self):
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], 'Пройдена!')

    def test_images_above_limit(self):
        checker_with_lower_limit = PresImageShareCheck(self.mock_file_info, limit=0.3)
        result = checker_with_lower_limit.check()
        self.assertFalse(result['score'])
        self.assertIn('Проверка не пройдена!', result['verdict'][0])

    def test_images_equal_limit(self):
        checker_with_equal_limit = PresImageShareCheck(self.mock_file_info, limit=0.67)
        result = checker_with_equal_limit.check()
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], 'Пройдена!')


if __name__ == '__main__':
    unittest.main()
