from app.main.checks.report_checks.page_counter import ReportPageCounter
from tests.util.report_file_utils import create_report_file_info

class TestReportPageCounterCheck:

    def test_01_valid_count(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "page_counter" / "valid.md")
        checker = ReportPageCounter(file_info, min_number=5, max_number=100)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_too_few_pages(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "page_counter" / "invalid.md")
        checker = ReportPageCounter(file_info, min_number=10, max_number=100)
        result = checker.check()
        assert result["score"] == 0.0
