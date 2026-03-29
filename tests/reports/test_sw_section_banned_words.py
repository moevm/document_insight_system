from app.main.checks.report_checks.sw_section_banned_words import SWSectionBannedWordsCheck

class TestSWSectionBannedWordsCheck:

    def test_01_valid_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_banned_words" / "valid.docx"
        checker = SWSectionBannedWordsCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Проверка пройдена!"

    def test_02_banned_word_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_banned_words" / "banned.docx"
        checker = SWSectionBannedWordsCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is False
        assert "содержит запрещенные слова" in result.result_str

    def test_03_some_chapter_with_banned_words(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_banned_words" / "some_banned.docx"
        checker = SWSectionBannedWordsCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is False
        assert "содержит запрещенные слова" in result.result_str