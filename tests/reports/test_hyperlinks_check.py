from unittest.mock import MagicMock

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
        assert result["score"] == 1.0
        assert "Проверка на гиперссылки пройдена" in result["verdict"][0]

    def test_02_invalid_document_with_hyperlinks(self, reports_fixture_dir):
        """Документ с активными гиперссылками -> результат неуспешен."""
        file_info = create_report_file_info(
            reports_fixture_dir / "hyperlinks_check" / "invalid.md"
        )
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()
        assert result["score"] < 1.0
        # В ответе должна быть информация о найденных гиперссылках
        assert "Гиперссылок" in result["verdict"][0]
        assert "https://example.com" in result["verdict"][0]

    def test_03_mailto_scheme_detected(self, reports_fixture_dir):
        """Проверяем, что и mailto: ссылки считаются активными."""
        file_info = create_report_file_info(
            reports_fixture_dir / "hyperlinks_check" / "invalid.md"
        )
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()
        assert result["score"] < 1.0
        assert "mailto" in result["verdict"][0].lower()

    def test_04_no_pdf_required(self, reports_fixture_dir):
        """Проверка не требует pdf-файла (работает с md-документами)."""
        file_info = create_report_file_info(
            reports_fixture_dir / "hyperlinks_check" / "valid.md"
        )
        checker = ReportHyperlinksCheck(file_info)
        result = checker.check()
        assert result["score"] == 1.0
