import unittest
from tests.tests_check.base_test import BaseTestCase
from app.main.checks.base_check import morph, answer
from app.main.checks.report_checks import ReportBannedWordsCheck

class TestReportBannedWordsCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.file_info['file'].page_counter.return_value = 5
        self.check = ReportBannedWordsCheck(file_info=self.file_info, words=["мы"], min_count=3, max_count=6)

    def test_check_not_enough_pages(self):
        self.file_info['file'].page_counter.return_value = 3
        result = self.check.check()
        self.assertEqual(result, answer(False, "В отчете недостаточно страниц. Нечего проверять."))

    def test_check_no_banned_words(self):
        self.file_info['file'].pdf_file.get_text_on_page.return_value = {
            1: "Пример текста без запретных слов.",
            2: "Еще один пример текста.",
            3: "Текст без запретных слов.",
            4: "Текст без запретных слов.",
            5: "Текст без запретных слов."
        }
        result = self.check.check()
        expected_output = 'Пройдена!'
        expected_result = answer(1, expected_output)
        self.assertEqual(result, expected_result)

    def test_check_with_banned_words_in_range(self):
        '''
        исходя из кода критерия, из каждой строки берется только одно вхождение каждого слова
        (создается множество), поэтому в этом примере запретных слов 5, что нарушает здравый смысл
        '''
        self.file_info['file'].pdf_file.get_text_on_page.return_value = {
            1: "мы мы мы",
            2: "мы мы",
            3: "мы",
            4: "мы мы",
            5: "мы"
        }
        result = self.check.check()
        expected_output = (
            '<b>Запрещенные слова: мы</b><br>Обнаружены запретные слова! <br><br>'
            'Страница №1:<br>Строка 1: мы мы мы <b>[мы]</b><br><br>'
            'Страница №2:<br>Строка 1: мы мы <b>[мы]</b><br><br>'
            'Страница №3:<br>Строка 1: мы <b>[мы]</b><br><br>'
            'Страница №4:<br>Строка 1: мы мы <b>[мы]</b><br><br>'
            'Страница №5:<br>Строка 1: мы <b>[мы]</b><br><br>'
        )
        expected_result = answer(0, expected_output)
        self.assertEqual(result['score'], expected_result['score'])
        self.assertEqual(result['verdict'][0], expected_result['verdict'][0])

    def test_check_with_banned_words_exceeding_max(self):
        self.file_info['file'].page_counter.return_value = 5
        self.file_info['file'].pdf_file.get_text_on_page.return_value = {
            1: "мы идем домой\nмы говорим о нас\nмы идем на работу",
            2: "мы любим природу\nмы читаем книги\nмы изучаем языки",
            3: "мы пишем код\nмы гуляем в парке\nмы играем в игры",
            4: "мы поем песни\nмы танцуем дома\nмы готовим ужин",
            5: "мы смотрим фильмы\nмы слушаем музыку\nмы общаемся с друзьями"
        }

        checker = ReportBannedWordsCheck(self.file_info, words=["мы"], min_count=3, max_count=6)
        result = checker.check()
        expected_output = (
            '<b>Запрещенные слова: мы</b><br>'
            'Обнаружены запретные слова! <br><br>'
            'Страница №1:<br>Строка 1: мы идем домой <b>[мы]</b><br>'
            'Строка 2: мы говорим о нас <b>[мы]</b><br>'
            'Строка 3: мы идем на работу <b>[мы]</b><br><br>'
            'Страница №2:<br>Строка 1: мы любим природу <b>[мы]</b><br>'
            'Строка 2: мы читаем книги <b>[мы]</b><br>'
            'Строка 3: мы изучаем языки <b>[мы]</b><br><br>'
            'Страница №3:<br>Строка 1: мы пишем код <b>[мы]</b><br>'
            'Строка 2: мы гуляем в парке <b>[мы]</b><br>'
            'Строка 3: мы играем в игры <b>[мы]</b><br><br>'
            'Страница №4:<br>Строка 1: мы поем песни <b>[мы]</b><br>'
            'Строка 2: мы танцуем дома <b>[мы]</b><br>'
            'Строка 3: мы готовим ужин <b>[мы]</b><br><br>'
            'Страница №5:<br>Строка 1: мы смотрим фильмы <b>[мы]</b><br>'
            'Строка 2: мы слушаем музыку <b>[мы]</b><br>'
            'Строка 3: мы общаемся с друзьями <b>[мы]</b><br><br>'
        )

        self.assertEqual(result, answer(0, expected_output))

if __name__ == '__main__':
    unittest.main()