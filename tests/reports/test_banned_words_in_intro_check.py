from app.main.checks.report_checks.banned_words_in_intro_check import BannedWordsInIntroCheck
from tests.util.report_file_utils import create_report_file_info


class TestBannedWordsInIntroReport:
    def test_01_docx_without_banword(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "banned_words_in_intro" / "valid.docx")
        checker = BannedWordsInIntroCheck(file_info)
        result = checker.check()

        assert result["score"] == 1

    def test_02_docx_with_banword(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "banned_words_in_intro" / "invalid.docx")
        checker = BannedWordsInIntroCheck(file_info)
        result = checker.check()

        assert result["score"] == 0
