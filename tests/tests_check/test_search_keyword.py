import unittest
from unittest.mock import Mock
from datetime import datetime
from app.main.checks.presentation_checks.search_keyword import SearchKeyWord

class TestSearchKeyWord(unittest.TestCase):

    def setUp(self):
        # Создаем заглушку для file_info
        self.file_info = {
            'file': Mock(),
            'filename': f'{datetime.now().year}ВКР111111ИВАНОВ.pdf',
            'pdf_id': '12345'
        }
        # Мокаем метод get_text_from_slides()
        self.file_info['file'].get_text_from_slides.return_value = [
            "Это текст первого слайда с актуальностью.",
            "Второй слайд без ключевого слова.",
            "Третий слайд с Актуальностью в заголовке.",
            "Четвертый слайд с актуальностью в конце текста",
        ]

    def test_find_existing_keyword(self):
        checker = SearchKeyWord(self.file_info, ["актуальность"])

        result = checker.check()

        self.assertTrue(result['score'])
        self.assertIn("Найден под номером:", result['verdict'][0])

    def test_find_non_existing_keyword(self):
        checker = SearchKeyWord(self.file_info, ["новое"])

        result = checker.check()

        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], "Слайд не найден")

    def test_multiple_key_words(self):
        checker = SearchKeyWord(self.file_info, ["актуальность", "важность"])

        result = checker.check()

        self.assertTrue(result['score'])
        self.assertIn("Найден под номером:", result['verdict'][0])

    def test_case_insensitivity(self):
        checker = SearchKeyWord(self.file_info, ["АКТУАЛЬНОСТЬ"])
        result = checker.check()

        self.assertTrue(result['score'])
        self.assertIn("Найден под номером:", result['verdict'][0])

if __name__ == '__main__':
    unittest.main()