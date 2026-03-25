import pytest
from app.main.checks.presentation_checks.further_dev import FurtherDev


class TestFurtherDev:

    def test_01_further_dev_found(self, further_dev_fixtures_dir):
        pptx_path = further_dev_fixtures_dir / "further_dev_found.pptx"
        checker = FurtherDev(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Направления развития найдены"

    def test_02_conclusion_not_exists(self, further_dev_fixtures_dir):
        pptx_path = further_dev_fixtures_dir / "no_conclusion.pptx"
        checker = FurtherDev(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert result.result_str == "Заключения не существует"

    def test_03_no_further_dev_in_conclusion(self, further_dev_fixtures_dir):
        pptx_path = further_dev_fixtures_dir / "no_further_dev.pptx"
        checker = FurtherDev(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "Направления развития не найдены" in result.result_str

    def test_04_custom_conclusion_title(self, further_dev_fixtures_dir):
        pptx_path = further_dev_fixtures_dir / "custom_conclusion.pptx"
        checker = FurtherDev(str(pptx_path), conclusion="Выводы и перспективы")
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Направления развития найдены"

    def test_05_indirect_indicators(self, further_dev_fixtures_dir):
        pptx_path = further_dev_fixtures_dir / "indirect_indicators.pptx"
        checker = FurtherDev(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Направления развития найдены"

    def test_06_different_formats(self, further_dev_fixtures_dir):
        ppt_path = further_dev_fixtures_dir / "further_dev_found.ppt"
        checker_ppt = FurtherDev(str(ppt_path))
        
        result_ppt = checker_ppt.check()
        
        assert result_ppt.status is True
        assert result_ppt.result_str == "Направления развития найдены"
        
        odp_path = further_dev_fixtures_dir / "further_dev_found.odp"
        checker_odp = FurtherDev(str(odp_path))
        
        result_odp = checker_odp.check()
        
        assert result_odp.status is True
        assert result_odp.result_str == "Направления развития найдены"