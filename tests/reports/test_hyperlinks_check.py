import pytest

from app.main.checks.report_checks.hyperlinks_check import ReportHyperlinksCheck
from tests.util.report_file_utils import create_report_file_info


class TestReportHyperlinksCheck:
    """Тесты проверки отсутствия активных гиперссылок во всей работе."""

    def test_01_valid_document_no_hyperlinks(self, reports_fixture_dir):
        """Валидный документ без активных гиперссылок -> проверка пройдена."""
        file_info = create_report_file_info(
            reports_fixture_dir / "hyperlinks_check" / "valid.md"
        )
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()

        assert result["score"] == 1

    def test_02_invalid_document_with_hyperlinks(self, reports_fixture_dir):
        """Документ с активными гиперссылками -> результат неуспешен."""
        file_info = create_report_file_info(
            reports_fixture_dir / "hyperlinks_check" / "invalid.md"
        )
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()

        assert result["score"] == 0
        assert "найдено" in result["verdict"][0].lower()
        assert "https://example.com" in result["verdict"][0]

    def test_03_mailto_detected(self, reports_fixture_dir):
        """Проверяем, что и mailto: ссылки считаются активными."""
        file_info = create_report_file_info(
            reports_fixture_dir / "hyperlinks_check" / "invalid.md"
        )
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()

        assert result["score"] == 0
        assert "mailto" in result["verdict"][0].lower()
    
    @pytest.mark.parametrize(
        "file", 
        [
            ("invalid_mailto.docx"),
            ("invalid_link_to_file.docx"),
            ("invalid_hyperlinks_in_text.docx"),
            ("invalid_hyperlinks_in_table.docx"),
            ("invalid_hyperlinks_in_img.docx"),
            ("invalid_hyperlinks_in_colo.docx"),
        ]
    )
    def test_05_invalid_docx_files(self, reports_fixture_dir, file):
        file_path = reports_fixture_dir / "hyperlinks_check" / file
        file_info = create_report_file_info(file_path)
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()
        
        assert result["score"] == 0
        assert "найдено активных" in result["verdict"][0].lower()
    
    def test_06_valid_docx(self, reports_fixture_dir):
        file_path = reports_fixture_dir / "hyperlinks_check" / "valid.docx"
        file_info = create_report_file_info(file_path)
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()
        
        assert result["score"] == 1
