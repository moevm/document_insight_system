import unittest
from unittest.mock import MagicMock

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.file_info = {
            'file': MagicMock(),
            'filename': 'test.pdf',
            'pdf_id': '1234',
            'file_type': {'report_type': 'VKR'}
        }
