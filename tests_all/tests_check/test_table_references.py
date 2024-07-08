import unittest
from unittest.mock import MagicMock, patch
from app.main.checks.report_checks.table_references import TableReferences
from app.main.checks.base_check import answer
from tests_all.tests_check.base_test import BaseTestCase

class TestTableReferences(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.mock_file = self.file_info['file']
        self.file_info['file'] = self.mock_file


    def test_invalid_references(self):
        self.mock_file.page_counter.return_value = 10
        self.mock_file.make_chapters.return_value = [
            {"child": [{"style": "ВКР_Подпись таблицы".lower(), "text": "Таблица 1 -- Пример таблицы", "number": 1}]}
        ]
        self.mock_file.paragraphs = ["Этот текст содержит неправильную ссылку на таблицу 2."]
        self.file_info['file'] = self.mock_file

        checker = TableReferences(file_info=self.file_info)
        result = checker.check()

        self.assertFalse(result['score'])
        self.assertIn('Упомянуты несуществующие таблицы:', result['verdict'][0])


if __name__ == '__main__':
    unittest.main()