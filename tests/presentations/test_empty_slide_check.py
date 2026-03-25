import pytest
from app.main.checks.presentation_checks.empty_slide_check import PresEmptySlideCheck


class TestPresEmptySlideCheck:

    def test_01_valid_presentation(self, presentations_fixtures_dir):
        pptx_path = presentations_fixtures_dir / "empty_slide_check" / "valid.pptx"
        checker = PresEmptySlideCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_02_detect_empty_slides(self, presentations_fixtures_dir):
        pptx_path = presentations_fixtures_dir / "empty_slide_check" / "with_empty_slides.pptx"
        checker = PresEmptySlideCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Не пройдена" in result.result_str
        assert "пустые слайды" in result.result_str
        assert "2" in result.result_str
        assert "4" in result.result_str

    def test_03_detect_title_only_slides(self, presentations_fixtures_dir):
        pptx_path = presentations_fixtures_dir / "empty_slide_check" / "with_title_only.pptx"
        checker = PresEmptySlideCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Не пройдена" in result.result_str
        assert "только заголовок" in result.result_str
        assert "1" in result.result_str
        assert "3" in result.result_str

    def test_04_images_and_tables_as_content(self, presentations_fixtures_dir):
        pptx_path = presentations_fixtures_dir / "empty_slide_check" / "with_images_tables.pptx"
        checker = PresEmptySlideCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_05_backup_slide_ignored(self, presentations_fixtures_dir):
        pptx_path = presentations_fixtures_dir / "empty_slide_check" / "with_backup_slide.pptx"
        checker = PresEmptySlideCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_06_unsupported_format(self, presentations_fixtures_dir):
        pdf_path = presentations_fixtures_dir / "empty_slide_check" / "empty.pdf"
        checker = PresEmptySlideCheck(str(pdf_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"