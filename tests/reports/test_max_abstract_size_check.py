from unittest.mock import MagicMock
from app.main.checks.report_checks.max_abstract_size_check import ReportMaxSizeOfAbstractCheck
from tests.util.report_file_utils import create_report_file_info

class TestReportMaxSizeOfAbstractCheck:

    def test_01_valid_size(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "max_abstract_size_check" / "valid.md")
        checker = ReportMaxSizeOfAbstractCheck(file_info, max_size=1)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_too_large(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "max_abstract_size_check" / "invalid.md")
        file_info['file'].make_headers = MagicMock(return_value=[
            {"name": "Реферат", "page": 4},
            {"name": "Abstract", "page": 10},
            {"name": "Содержание", "page": 11},
        ])
        checker = ReportMaxSizeOfAbstractCheck(file_info, max_size=1)
        result = checker.check()
        assert result["score"] == 0.0
