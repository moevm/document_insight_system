from unittest.mock import MagicMock
from app.main.checks.report_checks.banned_words_check import ReportBannedWordsCheck
from tests.util.report_file_utils import create_report_file_info

class TestReportBannedWordsCheck:

    def test_01_valid_document(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "banned_words_check" / "valid.md")
        checker = ReportBannedWordsCheck(file_info)
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "Clean text"})
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_banned_words_found(self, reports_fixture_dir):
        from app.main.checks.report_checks.style_check_settings import StyleCheckSettings
        orig_words = StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['banned_words']
        orig_min = StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['min_count_for_banned_words_check']
        StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['banned_words'] = ('bannedword',)
        StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['min_count_for_banned_words_check'] = 0

        try:
            file_info = create_report_file_info(reports_fixture_dir / "banned_words_check" / "invalid.md")
            checker = ReportBannedWordsCheck(file_info)
            file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "some bannedword text"})
            result = checker.check()
            assert result["score"] < 1.0
            assert "Обнаружены запретные слова" in result["verdict"][0]
        finally:
            StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['banned_words'] = orig_words
            StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['min_count_for_banned_words_check'] = orig_min

    def test_03_insufficient_pages(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "banned_words_check" / "valid.md")
        file_info['file'].page_counter = lambda: 3
        checker = ReportBannedWordsCheck(file_info)
        result = checker.check()
        assert result["score"] == 0.0
        assert "недостаточно страниц" in result["verdict"][0]

    def test_04_warned_words(self, reports_fixture_dir):
        from app.main.checks.report_checks.style_check_settings import StyleCheckSettings
        orig_words = StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['warned_words']
        StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['warned_words'] = ('warnword',)

        try:
            file_info = create_report_file_info(reports_fixture_dir / "banned_words_check" / "valid.md")
            checker = ReportBannedWordsCheck(file_info)
            file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value={1: "some warnword here"})
            result = checker.check()
            assert result["score"] == 1.0
            assert "потенциально опасные слова" in result["verdict"][0]
        finally:
            StyleCheckSettings.CONFIGS['VKR_HEADERS']['any_header']['warned_words'] = orig_words
