import unittest
from unittest.mock import patch, MagicMock
import os


from app.main.parser import parse
from app.utils.converter import convert_to
from app.main.reports.docx_uploader.docx_uploader import DocxUploader
from app.main.reports.md_uploader import MdUploader
from app.main.presentations.pptx.presentation_pptx import PresentationPPTX

class TestParseFunction(unittest.TestCase):

    @patch('app.utils.converter.convert_to')
    @patch('app.main.reports.docx_uploader.docx_uploader.DocxUploader')
    def test_parse_docx(self, MockDocxUploader, mock_convert_to):
        filepath = 'test.docx'
        pdf_filepath = 'test.pdf'
        mock_docx = MagicMock()
        MockDocxUploader.return_value = mock_docx

        result = parse(filepath, pdf_filepath)

        MockDocxUploader.assert_called_once_with()
        mock_docx.upload.assert_called_once_with(filepath, pdf_filepath)
        mock_docx.parse.assert_called_once()
        self.assertEqual(result, mock_docx)



if __name__ == '__main__':
    unittest.main()