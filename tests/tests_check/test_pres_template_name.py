import unittest
from app.main.checks.base_check import answer, BasePresCriterion
from app.main.checks.presentation_checks.template_name import PresTemplateNameCheck

class TestPresTemplateNameCheck(unittest.TestCase):

    def setUp(self):
        self.file_info = {
            'filename': "Презентация_ВКР_Иванов.pdf",
            'file': None,
            'pdf_id': '12345'
        }

    def test_correct_filename_format(self):
        checker = PresTemplateNameCheck(self.file_info)

        result = checker.check()

        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], "Пройдена!")

    def test_incorrect_filename_format(self):
        self.file_info['filename'] = "Презентация_ДИПЛОМ_Петров.pdf"

        checker = PresTemplateNameCheck(self.file_info)

        result = checker.check()

        self.assertFalse(result['score'])
        self.assertIn("не соответствует шаблону", result['verdict'][0])

    def test_empty_filename(self):
        self.file_info['filename'] = ""

        checker = PresTemplateNameCheck(self.file_info)

        result = checker.check()

        self.assertFalse(result['score'])
        self.assertIn("не соответствует шаблону", result['verdict'][0])

if __name__ == '__main__':
    unittest.main()

