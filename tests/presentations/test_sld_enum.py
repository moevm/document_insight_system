import pytest
from app.main.checks.presentation_checks.sld_enum import SldEnumCheck


class TestSldEnumCheck:

    def test_01_correct_enumeration(self, sld_enum_fixtures_dir):
        pptx_path = sld_enum_fixtures_dir / "correct_enumeration.pptx"
        checker = SldEnumCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_02_no_number_on_first_slide(self, sld_enum_fixtures_dir):
        pptx_path = sld_enum_fixtures_dir / "no_number_first_slide.pptx"
        checker = SldEnumCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Не пройдена" in result.result_str
        assert "1" in result.result_str

    def test_03_incorrect_enumeration_multiple_slides(self, sld_enum_fixtures_dir):
        pptx_path = sld_enum_fixtures_dir / "incorrect_enumeration.pptx"
        checker = SldEnumCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Не пройдена" in result.result_str
        assert "2" in result.result_str
        assert "3" in result.result_str
        assert "5" in result.result_str

    def test_04_numbers_not_starting_from_one(self, sld_enum_fixtures_dir):
        pptx_path = sld_enum_fixtures_dir / "not_starting_from_one.pptx"
        checker = SldEnumCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Не пройдена" in result.result_str
        assert "1" in result.result_str
        assert "2" in result.result_str
        assert "3" in result.result_str
        assert "4" in result.result_str

    def test_05_gap_in_enumeration(self, sld_enum_fixtures_dir):
        pptx_path = sld_enum_fixtures_dir / "gap_in_enumeration.pptx"
        checker = SldEnumCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Не пройдена" in result.result_str
        assert "3" in result.result_str
        assert "4" in result.result_str

    def test_06_different_number_formats(self, sld_enum_fixtures_dir):
        pptx_path = sld_enum_fixtures_dir / "different_formats.pptx"
        checker = SldEnumCheck(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Пройдена!"