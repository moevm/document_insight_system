import unittest
from app.main.checks.report_checks import ReportMaxSizeOfAbstractCheck
from tests.tests_check.base_test import BaseTestCase


class TestReportMaxSizeOfAbstractCheck(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.file_info['file'] = self.mock_file
        self.checker = ReportMaxSizeOfAbstractCheck(file_info=self.file_info, max_size=1)

    def test_abstract_and_referat_size_within_limit(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Реферат", "page": 1},
            {"name": "Abstract", "page": 2},
            {"name": "Содержание", "page": 3}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportMaxSizeOfAbstractCheck(file_info=self.file_info, max_size=1)
        result = self.checker.check()
        expected_output = "<br><br>Размеры разделов \"Реферат\" и \"Abstract\" соответствуют шаблону"
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_referat_exceeds_limit(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Реферат", "page": 1},
            {"name": "Abstract", "page": 3},
            {"name": "Содержание", "page": 4}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportMaxSizeOfAbstractCheck(file_info=self.file_info, max_size=1)
        result = self.checker.check()
        expected_output = "<br><br>Размер раздела \"Реферат\" равен 2 страницы, должен быть 1"
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_abstract_exceeds_limit(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Реферат", "page": 1},
            {"name": "Abstract", "page": 2},
            {"name": "Содержание", "page": 4}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportMaxSizeOfAbstractCheck(file_info=self.file_info, max_size=1)
        result = self.checker.check()
        expected_output = "<br><br>Размер раздела \"Abstract\" равен 2 страницы, должен быть 1"
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_both_exceed_limit(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Реферат", "page": 1},
            {"name": "Abstract", "page": 3},
            {"name": "Содержание", "page": 6}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportMaxSizeOfAbstractCheck(file_info=self.file_info, max_size=1)
        result = self.checker.check()
        expected_output = "<br><br>Размеры разделов \"Реферат\" и \"Abstract\" превышает максимальный размер"
        self.assertFalse(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)

    def test_no_referat_and_abstract(self):
        self.mock_file.make_headers.return_value = [
            {"name": "Содержание", "page": 1}
        ]
        self.file_info['file'] = self.mock_file
        self.checker = ReportMaxSizeOfAbstractCheck(file_info=self.file_info, max_size=1)
        self.checker.late_init()
        self.assertEqual(self.checker.referat_size, 0)
        self.assertEqual(self.checker.abstract_size, 0) #self.referat_size = abstract_page - referat_page = 1 (хотя Abstract не существует)
        result = self.checker.check()
        expected_output = "<br><br>Размеры разделов \"Реферат\" и \"Abstract\" соответствуют шаблону"
        self.assertTrue(result['score'])
        self.assertEqual(result['verdict'][0], expected_output)


if __name__ == '__main__':
    unittest.main()
