import unittest
from unittest.mock import MagicMock
# from ..base_check import BaseReportCriterion, answer, morph
# from your_module import ReportBannedWordsCheck
from document_insight_system.app.main.checks.base_check import morph
from document_insight_system.app.main.checks.report_checks import ReportBannedWordsCheck


class TestReportBannedWordsCheck(unittest.TestCase):
    def setUp(self):
        # Мокируем file_info и его методы
        self.file_info = MagicMock()
        self.file_info.page_counter.return_value = 5
        self.file_info.pdf_file.get_text_on_page.return_value = {
            1: "мы есть здесь\nмы есть там\nмы и мы и мы",
            2: "мы не есть\nне мы\n",
            3: "мы здесь\nмы там\nмы везде",
            4: "мы и вы\nмы и они",
            5: "они и мы\nвы и мы\nмы здесь"
        }

        # Мокируем morph.normal_forms для простоты
        morph.normal_forms = lambda word: [word]

    def test_no_banned_words(self):
        self.file_info.pdf_file.get_text_on_page.return_value = {
            1: "они есть здесь\nвы есть там\nмысли о нас",
            2: "мысли не есть\nне мысли\n",
            3: "они здесь\nвы там\nмысли везде",
            4: "вы и они\nмысли и они",
            5: "они и мысли\nвы и мысли\nмысли здесь"
        }

        check = ReportBannedWordsCheck(self.file_info)
        result = check.check()
        self.assertEqual(result['result'], 1)
        self.assertIn('Пройдена!', result['comment'])

    def test_banned_words_within_range(self):
        check = ReportBannedWordsCheck(self.file_info, min_count=3, max_count=6)
        result = check.check()
        self.assertEqual(result['result'], 0.5)
        self.assertIn('Обнаружены запретные слова!', result['comment'])

    def test_banned_words_above_range(self):
        self.file_info.pdf_file.get_text_on_page.return_value = {
            1: "мы есть здесь\nмы есть там\nмы и мы и мы",
            2: "мы не есть\nне мы\n",
            3: "мы здесь\nмы там\nмы везде",
            4: "мы и вы\nмы и они",
            5: "мы и мы\nмы и мы\nмы здесь"
        }

        check = ReportBannedWordsCheck(self.file_info, min_count=3, max_count=6)
        result = check.check()
        self.assertEqual(result['result'], 0)
        self.assertIn('Обнаружены запретные слова!', result['comment'])

    def test_insufficient_pages(self):
        self.file_info.page_counter.return_value = 3

        check = ReportBannedWordsCheck(self.file_info)
        result = check.check()
        self.assertEqual(result['result'], False)
        self.assertIn('В отчете недостаточно страниц. Нечего проверять.', result['comment'])


if __name__ == '__main__':
    unittest.main()
