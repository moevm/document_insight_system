from unittest.mock import MagicMock
from app.main.checks.report_checks.decimal_places import ReportDecimalPlacesCheck
from tests.util.report_file_utils import create_report_file_info

class TestReportDecimalPlacesCheck:

    def test_01_valid_places(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "decimal_places_check" / "valid.md")
        checker = ReportDecimalPlacesCheck(file_info, max_decimal_places=2, max_violations=0)
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "1.23"})
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_too_many_places(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "decimal_places_check" / "invalid.md")
        checker = ReportDecimalPlacesCheck(file_info, max_decimal_places=2, max_violations=0)
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "1.2345"})
        result = checker.check()
        assert result["score"] == 0.0

    def test_03_ignore_ip_address(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "decimal_places_check" / "valid.md")
        checker = ReportDecimalPlacesCheck(file_info, max_decimal_places=2, max_violations=0)
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "IP address 192.168.1.1 is here"})
        result = checker.check()
        assert result["score"] == 1.0

    def test_04_ignore_date(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "decimal_places_check" / "valid.md")
        checker = ReportDecimalPlacesCheck(file_info, max_decimal_places=2, max_violations=0)
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "Date 25.05.2023"})
        result = checker.check()
        assert result["score"] == 1.0

    def test_05_comma_separator(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "decimal_places_check" / "invalid.md")
        checker = ReportDecimalPlacesCheck(file_info, max_decimal_places=2, max_violations=0)
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "Value with comma 1,2345"})
        result = checker.check()
        assert result["score"] == 0.0
