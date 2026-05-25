import pytest
from app.main.checks.presentation_checks.title_format import TitleFormatCheck
from helpers import make_file_info, verdict_str


class TestTitleFormatCheck:

    def _make_checker(self, path, **kwargs):
        return TitleFormatCheck(make_file_info(str(path)), **kwargs)

    def test_01_all_titles_correct(self, title_format_fixtures_dir):
        checker = self._make_checker(title_format_fixtures_dir / "all_correct.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_02_slides_without_titles(self, title_format_fixtures_dir):
        checker = self._make_checker(title_format_fixtures_dir / "missing_titles.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Заголовки не найдены" in verdict_str(result)
        assert "2" in verdict_str(result)
        assert "4" in verdict_str(result)

    def test_03_titles_exceeding_two_lines(self, title_format_fixtures_dir):
        checker = self._make_checker(title_format_fixtures_dir / "exceeded_lines.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Превышение длины" in verdict_str(result)
        assert "1" in verdict_str(result)
        assert "3" in verdict_str(result)

    def test_04_combined_issues(self, title_format_fixtures_dir):
        checker = self._make_checker(title_format_fixtures_dir / "combined_issues.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Заголовки не найдены" in verdict_str(result)
        assert "2" in verdict_str(result)
        assert "4" in verdict_str(result)
        assert "Превышение длины" in verdict_str(result)
        assert "5" in verdict_str(result)

    def test_05_special_characters_handling(self, title_format_fixtures_dir):
        checker = self._make_checker(title_format_fixtures_dir / "special_chars.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Превышение длины" in verdict_str(result)
        assert "2" in verdict_str(result)
        assert "3" in verdict_str(result)

    def test_06_empty_lines_after_split(self, title_format_fixtures_dir):
        checker = self._make_checker(title_format_fixtures_dir / "empty_lines.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"