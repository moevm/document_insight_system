from unittest.mock import MagicMock
from app.main.checks.report_checks.image_share_check import ReportImageShareCheck
from tests.util.report_file_utils import create_report_file_info

class TestReportImageShareCheck:

    def test_01_valid_share(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "image_share_check" / "valid.md")
        checker = ReportImageShareCheck(file_info, limit=0.5)
        file_info['file'].pdf_file.page_images = MagicMock(return_value=100)
        file_info['file'].pdf_file.page_height = MagicMock(return_value=1000)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_too_many_images(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "image_share_check" / "invalid.md")
        checker = ReportImageShareCheck(file_info, limit=0.1)
        file_info['file'].pdf_file.page_images = MagicMock(return_value=500)
        file_info['file'].pdf_file.page_height = MagicMock(return_value=1000)
        result = checker.check()
        assert result["score"] == 0.0
        assert "документа без учета приложения" in result["verdict"][0]
