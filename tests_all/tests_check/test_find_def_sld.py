import unittest
from unittest.mock import MagicMock
from app.main.checks.presentation_checks.find_def_sld import FindDefSld

class TestFindDefSld(unittest.TestCase):

    def setUp(self):
        self.mock_file_info = {
            'file': MagicMock(),
            'filename': 'test_presentation.pptx',
            'pdf_id': '12345',
            'presentation_name': 'test_presentation.pptx'
        }
        self.key_slide = "Key Slide"

        self.mock_titles = [
            "Introduction",
            "Key Slide Overview",
            "Details of Key Slide",
            "Conclusion"
        ]

        self.mock_file_info['file'].get_titles = MagicMock(return_value=self.mock_titles)
        self.mock_file_info['file'].found_index = {}

        self.checker = FindDefSld(self.mock_file_info, self.key_slide)

    def test_find_key_slide(self):
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertIn("Найден под номером: ", result['verdict'][0])
        self.assertIn('2', result['verdict'][0])
        self.assertIn('3', result['verdict'][0])

    def test_key_slide_not_found(self):
        self.checker.type_of_slide = "Nonexistent Slide"
        result = self.checker.check()
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], 'Слайд не найден')

    def test_key_slide_case_insensitive(self):
        self.checker.type_of_slide = "key slide"
        result = self.checker.check()
        self.assertTrue(result['score'])
        self.assertIn("Найден под номером: ", result['verdict'][0])
        self.assertIn('2', result['verdict'][0])
        self.assertIn('3', result['verdict'][0])

    def test_save_found_indices(self):
        self.checker.check()
        self.assertIn("Key Slide", self.mock_file_info['file'].found_index)
        self.assertEqual(self.mock_file_info['file'].found_index["Key Slide"], [2, 3])

if __name__ == "__main__":
    unittest.main()
