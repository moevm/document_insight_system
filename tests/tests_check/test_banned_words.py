import unittest
from unittest.mock import MagicMock
from app.main.checks.presentation_checks.banned_words import PresBannedWordsCheck
from app.main.checks.base_check import morph

class TestPresBannedWordsCheck(unittest.TestCase):

    def setUp(self):
        self.mock_file_info = {
            'file': MagicMock(),
            'filename': 'test_presentation.pptx',
            'pdf_id': '12345'
        }

        self.mock_text_slides = [
            "Это пример текста на первом слайде",
            "Запрещенное слово тут",
            "Еще один пример текста на слайде",
            "Снова запрещенное слово на слайде",
            "Обычный текст без запрещенных слов"
        ]

        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=self.mock_text_slides)
        self.checker = PresBannedWordsCheck(self.mock_file_info, words=['запрещенное', 'слово'], min_count=1, max_count=3)

    def test_no_banned_words(self):
        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=[
            "Просто пример текста."
        ])
        result = self.checker.check()
        self.assertEqual(result['score'], 1)
        self.assertEqual(result['verdict'][0], "Пройдена!")

    def test_banned_words_below_min_count(self):
        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=[
            "Запрещенное слово тут",
            "Еще один пример текста",
            "Снова запрещенное слово"
        ])
        self.checker = PresBannedWordsCheck(self.mock_file_info, words=['запрещенное', 'слово'], min_count=3, max_count=6)
        result = self.checker.check()
        self.assertEqual(result['score'], 1.0)
        self.assertIn("Обнаружены запретные слова!", result['verdict'][0])

    def test_banned_words_above_max_count(self):
        self.mock_file_info['file'].get_text_from_slides = MagicMock(return_value=[
            "Запрещенное слово тут",
            "Еще одно запрещенное слово тут",
            "Снова запрещенное слово",
            "Запрещенное слово тут снова"
        ])
        result = self.checker.check()
        self.assertEqual(result['score'], 0)
        self.assertIn("Обнаружены запретные слова!", result['verdict'][0])


if __name__ == "__main__":
    unittest.main()
