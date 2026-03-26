import pytest

from app.main.checks.report_checks.template_name import ReportTemplateNameCheck


class TestReportTemplateNameCheck:

    def test_01_valid_filename(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "template_name" / "2026ВКР123456ИВАНОВ.docx"
        checker = ReportTemplateNameCheck(report_path)
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_02_invalid_filename(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "template_name" / "2025ВКР123IVANOV.docx"
        checker = ReportTemplateNameCheck(report_path)
        result = checker.check()

        assert result.status is False
        assert "2025ВКР123IVANOV" in result.result_str