import pytest

from app.main.checks.report_checks.banned_words_in_intro_check import BannedWordsInIntroCheck
from tests.util.report_file_utils import create_report_file_info


class TestBannedWordsInIntroReport:
    report_dirs = "banned_words_in_intro"

    @pytest.mark.parametrize(
        "file, excepted_score",
        [
            ("valid.docx", 1),
            ("invalid.docx", 0),
            ("valid.md", 1),
            ("invalid.md", 0),
        ],
    )
    def test_01_with_and_without_banword(self, reports_fixture_dir, file, excepted_score):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dirs / file)
        checker = BannedWordsInIntroCheck(file_info)
        result = checker.check()

        assert result["score"] == excepted_score
