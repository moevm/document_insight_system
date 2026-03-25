import pytest
from app.main.checks.presentation_checks.image_capture import PresImageCaptureCheck


class TestPresImageCaptureCheck:

    def test_01_all_images_have_correct_captions(self, image_capture_fixtures_dir):
        pptx_path = image_capture_fixtures_dir / "all_correct.pptx"
        checker = PresImageCaptureCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert "Пройдена" in result.result_str

    def test_02_images_without_correct_caption(self, image_capture_fixtures_dir):
        pptx_path = image_capture_fixtures_dir / "without_correct_caption.pptx"
        checker = PresImageCaptureCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "не содержат слова" in result.result_str
        assert "3" in result.result_str
        assert "5" in result.result_str

    def test_03_images_on_slides_without_text(self, image_capture_fixtures_dir):
        pptx_path = image_capture_fixtures_dir / "no_text_slides.pptx"
        checker = PresImageCaptureCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert "необязательны" in result.result_str
        assert "7" in result.result_str
        assert "9" in result.result_str

    def test_04_mixed_case(self, image_capture_fixtures_dir):
        pptx_path = image_capture_fixtures_dir / "mixed_case.pptx"
        checker = PresImageCaptureCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "не содержат слова" in result.result_str
        assert "3" in result.result_str
        assert "необязательны" in result.result_str
        assert "4" in result.result_str
        assert "5" in result.result_str

    def test_05_caption_matches_slide_title(self, image_capture_fixtures_dir):
        pptx_path = image_capture_fixtures_dir / "caption_matches_title.pptx"
        checker = PresImageCaptureCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert "Пройдена" in result.result_str

    def test_06_multiple_captions_on_one_slide(self, image_capture_fixtures_dir):
        pptx_path = image_capture_fixtures_dir / "multiple_captions.pptx"
        checker = PresImageCaptureCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "не содержат слова" in result.result_str
        assert "12" in result.result_str