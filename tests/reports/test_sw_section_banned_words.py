from app.main.checks.report_checks.sw_section_banned_words import SWSectionBannedWordsCheck
from tests.util import create_report_file_info


class TestSWSectionBannedWordsCheck:

    def test_01_valid_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_banned_words" / "valid.md"
        checker = SWSectionBannedWordsCheck(create_report_file_info(report_path), "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result["score"] == 1.0
        assert result["verdict"][0] == "Проверка пройдена!"

    def test_02_banned_word_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_banned_words" / "banned.md"
        checker = SWSectionBannedWordsCheck(create_report_file_info(report_path), "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result["score"] == 0.0
        assert "содержит запрещенные слова" in result["verdict"][0]

    def test_03_some_chapter_with_banned_words(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_banned_words" / "some_banned.md"
        checker = SWSectionBannedWordsCheck(create_report_file_info(report_path), "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result["score"] == 0.0
        assert "содержит запрещенные слова" in result["verdict"][0]