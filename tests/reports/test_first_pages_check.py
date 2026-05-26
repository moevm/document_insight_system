from app.main.checks.report_checks.first_pages_check import ReportFirstPagesCheck
from tests.util.report_file_utils import create_report_file_info

class TestReportFirstPagesCheck:

    def test_01_valid_document(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "first_pages_check" / "valid.md")
        checker = ReportFirstPagesCheck(file_info)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_missing_pages(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "first_pages_check" / "invalid.md")
        checker = ReportFirstPagesCheck(file_info)
        result = checker.check()
        assert result["score"] == 0.0
