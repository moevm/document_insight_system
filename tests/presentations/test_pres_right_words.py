import pytest
from app.main.checks.presentation_checks.right_words import PresRightWordsCheck


class TestPresRightWordsCheck:

    def test_01_all_patterns_found(self, right_words_fixtures_dir):
        pptx_path = right_words_fixtures_dir / "all_patterns_found.pptx"
        patterns = ['актуальн', 'практическ', 'научн']
        checker = PresRightWordsCheck(str(pptx_path), patterns)
        
        result = checker.check()
        
        assert result.status == 1
        assert result.result_str == "Пройдена!"

    def test_02_some_patterns_not_found(self, right_words_fixtures_dir):
        pptx_path = right_words_fixtures_dir / "some_patterns_not_found.pptx"
        patterns = ['актуальн', 'практическ', 'научн', 'эксперимент']
        checker = PresRightWordsCheck(str(pptx_path), patterns)
        
        result = checker.check()
        
        assert result.status == 0
        assert "Не найдены" in result.result_str
        assert "научн" in result.result_str
        assert "эксперимент" in result.result_str

    def test_03_case_insensitive_search(self, right_words_fixtures_dir):
        pptx_path = right_words_fixtures_dir / "case_insensitive.pptx"
        patterns = ['актуальность']
        checker = PresRightWordsCheck(str(pptx_path), patterns)
        
        result = checker.check()
        
        assert result.status == 1
        assert result.result_str == "Пройдена!"

    def test_04_regex_pattern(self, right_words_fixtures_dir):
        pptx_path = right_words_fixtures_dir / "regex_pattern.pptx"
        patterns = ['\\d{4}']
        checker = PresRightWordsCheck(str(pptx_path), patterns)
        
        result = checker.check()
        
        assert result.status == 1
        assert result.result_str == "Пройдена!"

    def test_05_skip_title_slide(self, right_words_fixtures_dir):
        pptx_path = right_words_fixtures_dir / "title_slide_only.pptx"
        patterns = ['актуальность']
        checker = PresRightWordsCheck(str(pptx_path), patterns)
        
        result = checker.check()
        
        assert result.status == 0
        assert "Не найдены" in result.result_str
        assert "актуальность" in result.result_str

    def test_06_empty_patterns_list(self, right_words_fixtures_dir):
        pptx_path = right_words_fixtures_dir / "empty_patterns.pptx"
        patterns = []
        checker = PresRightWordsCheck(str(pptx_path), patterns)
        
        result = checker.check()
        
        assert result.status == 1
        assert result.result_str == "Пройдена!"