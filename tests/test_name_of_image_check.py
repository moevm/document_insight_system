import pytest
from app.main.checks.presentation_checks.image_capture import PresImageCaptureCheck
from helpers import make_file_info, verdict_str


class TestPresImageCaptureCheck:

    def _make_checker(self, path, **kwargs):
        return PresImageCaptureCheck(make_file_info(str(path)), **kwargs)

    def test_01_all_images_have_correct_captions(self, image_capture_fixtures_dir):
        checker = self._make_checker(image_capture_fixtures_dir / "all_correct.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert "Пройдена" in verdict_str(result)

    def test_02_images_without_correct_caption(self, image_capture_fixtures_dir):
        checker = self._make_checker(image_capture_fixtures_dir / "without_correct_caption.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "не содержат слова" in verdict_str(result)
        assert "3" in verdict_str(result)
        assert "5" in verdict_str(result)

    def test_03_images_on_slides_without_text(self, image_capture_fixtures_dir):
        checker = self._make_checker(image_capture_fixtures_dir / "no_text_slides.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert "необязательны" in verdict_str(result)
        assert "7" in verdict_str(result)
        assert "9" in verdict_str(result)

    def test_04_mixed_case(self, image_capture_fixtures_dir):
        checker = self._make_checker(image_capture_fixtures_dir / "mixed_case.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "не содержат слова" in verdict_str(result)
        assert "3" in verdict_str(result)
        assert "необязательны" in verdict_str(result)
        assert "4" in verdict_str(result)
        assert "5" in verdict_str(result)

    def test_05_caption_matches_slide_title(self, image_capture_fixtures_dir):
        checker = self._make_checker(image_capture_fixtures_dir / "caption_matches_title.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert "Пройдена" in verdict_str(result)

    def test_06_multiple_captions_on_one_slide(self, image_capture_fixtures_dir):
        checker = self._make_checker(image_capture_fixtures_dir / "multiple_captions.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "не содержат слова" in verdict_str(result)
        assert "12" in verdict_str(result)