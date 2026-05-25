import pytest
from app.main.checks.presentation_checks.sld_enum import SldEnumCheck
from helpers import make_file_info, verdict_str


class TestSldEnumCheck:

    def _make_checker(self, path, **kwargs):
        return SldEnumCheck(make_file_info(str(path)), **kwargs)

    def test_01_correct_enumeration(self, sld_enum_fixtures_dir):
        checker = self._make_checker(sld_enum_fixtures_dir / "correct_enumeration.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"

    def test_02_no_number_on_first_slide(self, sld_enum_fixtures_dir):
        checker = self._make_checker(sld_enum_fixtures_dir / "no_number_first_slide.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не пройдена" in verdict_str(result)
        assert "1" in verdict_str(result)

    def test_03_incorrect_enumeration_multiple_slides(self, sld_enum_fixtures_dir):
        checker = self._make_checker(sld_enum_fixtures_dir / "incorrect_enumeration.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не пройдена" in verdict_str(result)
        assert "2" in verdict_str(result)
        assert "3" in verdict_str(result)
        assert "5" in verdict_str(result)

    def test_04_numbers_not_starting_from_one(self, sld_enum_fixtures_dir):
        checker = self._make_checker(sld_enum_fixtures_dir / "not_starting_from_one.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не пройдена" in verdict_str(result)
        assert "1" in verdict_str(result)
        assert "2" in verdict_str(result)
        assert "3" in verdict_str(result)
        assert "4" in verdict_str(result)

    def test_05_gap_in_enumeration(self, sld_enum_fixtures_dir):
        checker = self._make_checker(sld_enum_fixtures_dir / "gap_in_enumeration.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Не пройдена" in verdict_str(result)
        assert "3" in verdict_str(result)
        assert "4" in verdict_str(result)

    def test_06_different_number_formats(self, sld_enum_fixtures_dir):
        checker = self._make_checker(sld_enum_fixtures_dir / "different_formats.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Пройдена!"