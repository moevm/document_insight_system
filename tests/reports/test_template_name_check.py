import pytest

from app.main.checks.report_checks.template_name import ReportTemplateNameCheck


class TestReportTemplateNameCheck:

    def test_01_valid_filename(self, reports_fixture_dir):
        filename =  "valid.docx"
        file_info = {
            'file': None,
            'filename': filename,
            'pdf_id': None,
            'file_type': 'docx'
        }
        checker = ReportTemplateNameCheck(file_info)
        result = checker.check()

        assert result['score'] == 1.0
        assert result['verdict'][0] == "Пройдена!"

    def test_02_invalid_filename(self, reports_fixture_dir):
        filename =  "2025ВКР123IVANOV.docx"
        file_info = {
            'file': None,
            'filename': filename,
            'pdf_id': None,
            'file_type': 'docx'
        }
        checker = ReportTemplateNameCheck(file_info)
        result = checker.check()

        assert result['score'] == 0.0
        assert "2025ВКР123IVANOV" in result['verdict'][0]