import pytest
from app.main.checks.presentation_checks.title_format import TitleFormatCheck


class TestTitleFormatCheck:

    def test_01_all_titles_correct(self, title_format_fixtures_dir):
        pptx_path = title_format_fixtures_dir / "all_correct.pptx"
        checker = TitleFormatCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_02_slides_without_titles(self, title_format_fixtures_dir):
        pptx_path = title_format_fixtures_dir / "missing_titles.pptx"
        checker = TitleFormatCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Заголовки не найдены" in result.result_str
        assert "2" in result.result_str
        assert "4" in result.result_str

    def test_03_titles_exceeding_two_lines(self, title_format_fixtures_dir):
        pptx_path = title_format_fixtures_dir / "exceeded_lines.pptx"
        checker = TitleFormatCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Превышение длины" in result.result_str
        assert "1" in result.result_str
        assert "3" in result.result_str

    def test_04_combined_issues(self, title_format_fixtures_dir):
        pptx_path = title_format_fixtures_dir / "combined_issues.pptx"
        checker = TitleFormatCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Заголовки не найдены" in result.result_str
        assert "2" in result.result_str
        assert "4" in result.result_str
        assert "Превышение длины" in result.result_str
        assert "5" in result.result_str

    def test_05_special_characters_handling(self, title_format_fixtures_dir):
        pptx_path = title_format_fixtures_dir / "special_chars.pptx"
        checker = TitleFormatCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Превышение длины" in result.result_str
        assert "2" in result.result_str
        assert "3" in result.result_str

    def test_06_empty_lines_after_split(self, title_format_fixtures_dir):
        pptx_path = title_format_fixtures_dir / "empty_lines.pptx"
        checker = TitleFormatCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"