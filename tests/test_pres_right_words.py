import pytest
from app.main.checks.presentation_checks.right_words import PresRightWordsCheck
from helpers import make_file_info, verdict_str


class TestPresRightWordsCheck:

    def _make_checker(self, path, patterns, **kwargs):
        return PresRightWordsCheck(make_file_info(str(path)), patterns, **kwargs)

    def test_01_all_patterns_found(self, right_words_fixtures_dir):
        checker = self._make_checker(right_words_fixtures_dir / "all_patterns_found.pptx", ['актуальн', 'практическ', 'научн'])
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_02_some_patterns_not_found(self, right_words_fixtures_dir):
        checker = self._make_checker(right_words_fixtures_dir / "some_patterns_not_found.pptx", ['актуальн', 'практическ', 'научн', 'эксперимент'])
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не найдены" in verdict_str(result)
        assert "научн" in verdict_str(result)
        assert "эксперимент" in verdict_str(result)

    def test_03_case_insensitive_search(self, right_words_fixtures_dir):
        checker = self._make_checker(right_words_fixtures_dir / "case_insensitive.pptx", ['актуальность'])
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_04_regex_pattern(self, right_words_fixtures_dir):
        checker = self._make_checker(right_words_fixtures_dir / "regex_pattern.pptx", ['\\d{4}'])
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_05_skip_title_slide(self, right_words_fixtures_dir):
        checker = self._make_checker(right_words_fixtures_dir / "title_slide_only.pptx", ['актуальность'])
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не найдены" in verdict_str(result)
        assert "актуальность" in verdict_str(result)

    def test_06_empty_patterns_list(self, right_words_fixtures_dir):
        checker = self._make_checker(right_words_fixtures_dir / "empty_patterns.pptx", [])
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"