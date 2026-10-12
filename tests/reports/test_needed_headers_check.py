from app.main.checks.report_checks.structure_check import ReportStructureCheck
from app.main.checks.report_checks.style_check_settings import StyleCheckSettings
from tests.util.report_file_utils import create_report_file_info


class TestReportNeededHeadersCheck:
    def test_01_valid_document(self, reports_fixture_dir, monkeypatch):
        monkeypatch.setitem(StyleCheckSettings.VKR_CONFIG["any_header"], "check_sequence", False)

        file_info = create_report_file_info(reports_fixture_dir / "needed_headers_check" / "valid.md")
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReportStructureCheck(file_info)
        result = checker.check()
        assert result["score"] == 1.0
        assert "Все необходимые заголовки обнаружены" in result["verdict"][0]

    def test_02_missing_headers(self, reports_fixture_dir, monkeypatch):
        monkeypatch.setitem(StyleCheckSettings.VKR_CONFIG["any_header"], "check_sequence", False)

        file_info = create_report_file_info(reports_fixture_dir / "needed_headers_check" / "invalid.md")
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReportStructureCheck(file_info)
        result = checker.check()
        assert result["score"] == 0.0
        assert "Не найдены следующие обязательные заголовки" in result["verdict"][0]

    def test_03_insufficient_pages(self, reports_fixture_dir, monkeypatch):
        monkeypatch.setitem(StyleCheckSettings.VKR_CONFIG["any_header"], "check_sequence", False)

        file_info = create_report_file_info(reports_fixture_dir / "needed_headers_check" / "valid.md")
        file_info['file'].page_counter = lambda: 3
        checker = ReportStructureCheck(file_info)
        result = checker.check()
        assert result["score"] == 0.0
        assert "недостаточно страниц" in result["verdict"][0]
