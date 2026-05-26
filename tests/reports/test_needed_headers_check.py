from app.main.checks.report_checks.needed_headers_check import ReportNeededHeadersCheck
from tests.util.report_file_utils import create_report_file_info

class TestReportNeededHeadersCheck:

    def test_01_valid_document(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "needed_headers_check" / "valid.md")
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReportNeededHeadersCheck(file_info)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_missing_headers(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "needed_headers_check" / "invalid.md")
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReportNeededHeadersCheck(file_info)
        result = checker.check()
        assert result["score"] == 0.0
