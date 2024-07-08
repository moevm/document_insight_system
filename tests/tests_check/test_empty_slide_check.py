import unittest
from unittest.mock import MagicMock
from app.main.checks.presentation_checks.empty_slide_check import PresEmptySlideCheck
from app.utils.parse_for_html import format_header


class TestPresEmptySlideCheck(unittest.TestCase):

    def setUp(self):
        self.mock_file_info = {
            'file': MagicMock(),
            'filename': 'test_presentation.pptx',
            'pdf_id': '12345',
            'presentation_name': 'test_presentation.pptx'
        }

        self.mock_text_slides = [
            "",  # Пустой слайд
            "Title Slide\nContent on Slide",  # Слайд с заголовком и контентом
            "Only Title Slide\n",  # Слайд только с заголовком
            "",  # Пустой слайд
        ]
        self.mock_titles = [
            "Title Slide",
            "Title Slide",
            "Only Title Slide",
            ""
        ]

        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=self.mock_text_slides)
        self.mock_file_info['file'].get_titles = MagicMock(return_value=self.mock_titles)
        self.mock_file_info['file'].slides = [MagicMock() for _ in self.mock_text_slides]

        for slide in self.mock_file_info['file'].slides:
            slide.get_images = MagicMock(return_value=[])
            slide.get_table = MagicMock(return_value=None)

        self.checker = PresEmptySlideCheck(self.mock_file_info)

    def test_empty_slides(self):
        result = self.checker.check()
        self.assertEqual(result['score'], 0)
        self.assertIn("Не пройдена! Обнаружены пустые слайды:", result['verdict'][0])

    def test_only_title_slides(self):
        self.mock_text_slides = [
            "Title Slide\n",
            "Title Slide\nContent on Slide",
            "Only Title Slide\n",
            "Another Title\nContent"
        ]
        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=self.mock_text_slides)
        self.mock_file_info['file'].get_titles = MagicMock(return_value=self.mock_titles)

        result = self.checker.check()
        self.assertEqual(result['score'], 0)
        self.assertIn("Не пройдена! Обнаружены слайды, в которых присутствует только заголовок:", result['verdict'][0])

    def test_mixed_empty_and_title_slides(self):
        self.mock_text_slides = [
            "",
            "Title Slide\nContent on Slide",
            "Only Title Slide\n",
            "",
        ]
        self.mock_titles = [
            "Empty Slide",
            "Title Slide",
            "Only Title Slide",
            "Empty Slide"
        ]
        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=self.mock_text_slides)
        self.mock_file_info['file'].get_titles = MagicMock(return_value=self.mock_titles)

        result = self.checker.check()
        self.assertEqual(result['score'], 0)
        self.assertIn("Не пройдена! Обнаружены пустые слайды:", result['verdict'][0])
        self.assertIn("также обнаружены слайды, в которых присутствует только заголовок:", result['verdict'][0])

    def test_no_empty_or_title_only_slides(self):
        self.mock_text_slides = [
            "Title Slide\nContent on Slide",
            "Another Title\nContent",
            "Content without Title",
        ]
        self.mock_titles = [
            "Title Slide",
            "Another Title",
            ""
        ]
        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=self.mock_text_slides)
        self.mock_file_info['file'].get_titles = MagicMock(return_value=self.mock_titles)

        result = self.checker.check()
        self.assertEqual(result['score'], 1)
        self.assertEqual(result['verdict'][0], "Пройдена!")


if __name__ == "__main__":
    unittest.main()
