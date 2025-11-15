import unittest
from app.main.checks.report_checks import BannedWordsInLiteratureCheck
from tests.tests_check.base_test import BaseTestCase
from app.main.checks.base_check import morph, answer

morph.normal_forms = lambda word: [word]

class TestBannedWordsInLiteratureCheck(BaseTestCase):

    def test_check_with_no_banned_words(self):
        self.file_info['file'].page_counter.return_value = 10
        self.file_info['file'].find_literature_vkr.return_value = {"number": 1, "child": [{"number": 2, "text": "This is a good source."}]}
        self.file_info['file'].find_literature_page.return_value = 10

        checker = BannedWordsInLiteratureCheck(self.file_info)
        result = checker.check()

        self.assertEqual(result, answer(True, "Пройдена!"))

    def test_check_with_banned_words(self):
        self.file_info['file'].page_counter.return_value = 10
        self.file_info['file'].find_literature_vkr.return_value = {"number": 1, "child": [{"number": 2, "text": "Source from wikipedia."}]}
        self.file_info['file'].find_literature_page.return_value = 10

        checker = BannedWordsInLiteratureCheck(self.file_info)
        result = checker.check()

        expected_output = (
            'Есть запрещенные слова в списке источников '
            '[\'<a href="/get_pdf/1234#page=10"target="_blank" rel="noopener">10<a>\']:<br><br>'
            'Абзац 1: wikipedia.<br>'
        )

        self.assertEqual(result, answer(False, expected_output))

    def test_check_not_enough_pages(self):
        self.file_info['file'].page_counter.return_value = 3

        checker = BannedWordsInLiteratureCheck(self.file_info)
        result = checker.check()

        self.assertEqual(result, answer(False, "В отчете недостаточно страниц. Нечего проверять."))

if __name__ == '__main__':
    unittest.main()
