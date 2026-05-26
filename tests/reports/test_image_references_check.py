from unittest.mock import MagicMock
from app.main.checks.report_checks.image_references import ImageReferences
from tests.util.report_file_utils import create_report_file_info

class TestImageReferencesCheck:

    def test_01_valid_references(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "image_references" / "valid.md")
        checker = ImageReferences(file_info, image_style="вкр_подпись для рисунков")
        file_info['file'].pdf_file.pdf_file.get_page_images = MagicMock(return_value=[1])
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_missing_references(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "image_references" / "invalid.md")
        checker = ImageReferences(file_info, image_style="вкр_подпись для рисунков")
        file_info['file'].pdf_file.pdf_file.get_page_images = MagicMock(return_value=[1, 2])
        result = checker.check()
        assert result["score"] == 0.0
