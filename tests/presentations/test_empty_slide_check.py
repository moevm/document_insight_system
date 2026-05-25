import pytest
from app.main.checks.presentation_checks.empty_slide_check import PresEmptySlideCheck
from helpers import make_file_info, verdict_str


class TestPresEmptySlideCheck:

    def _make_checker(self, path, **kwargs):
        return PresEmptySlideCheck(make_file_info(str(path)), **kwargs)

    def test_01_valid_presentation(self, presentations_fixtures_dir):
        checker = self._make_checker(presentations_fixtures_dir / "empty_slide_check" / "valid.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_02_detect_empty_slides(self, presentations_fixtures_dir):
        checker = self._make_checker(presentations_fixtures_dir / "empty_slide_check" / "with_empty_slides.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не пройдена" in verdict_str(result)
        assert "пустые слайды" in verdict_str(result)
        assert "2" in verdict_str(result)
        assert "4" in verdict_str(result)

    def test_03_detect_title_only_slides(self, presentations_fixtures_dir):
        checker = self._make_checker(presentations_fixtures_dir / "empty_slide_check" / "with_title_only.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не пройдена" in verdict_str(result)
        assert "только заголовок" in verdict_str(result)
        assert "1" in verdict_str(result)
        assert "3" in verdict_str(result)

    def test_04_images_and_tables_as_content(self, presentations_fixtures_dir):
        checker = self._make_checker(presentations_fixtures_dir / "empty_slide_check" / "with_images_tables.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_05_backup_slide_ignored(self, presentations_fixtures_dir):
        checker = self._make_checker(presentations_fixtures_dir / "empty_slide_check" / "with_backup_slide.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_06_unsupported_format(self, presentations_fixtures_dir):
        checker = self._make_checker(presentations_fixtures_dir / "empty_slide_check" / "empty.pdf")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"
