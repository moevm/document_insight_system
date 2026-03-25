import pytest
from app.main.checks.presentation_checks.sld_similarity import SldSimilarity


class TestSldSimilarity:

    def test_01_full_compliance(self, sld_similarity_fixtures_dir):
        pptx_path = sld_similarity_fixtures_dir / "full_compliance.pptx"
        checker = SldSimilarity(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True

    def test_02_partial_compliance_above_threshold(self, sld_similarity_fixtures_dir):
        pptx_path = sld_similarity_fixtures_dir / "partial_compliance.pptx"
        checker = SldSimilarity(str(pptx_path), min_percent=70)
        
        result = checker.check()
        
        assert result.status is True

    def test_03_compliance_below_threshold(self, sld_similarity_fixtures_dir):
        pptx_path = sld_similarity_fixtures_dir / "low_compliance.pptx"
        checker = SldSimilarity(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False

    def test_04_custom_section_titles(self, sld_similarity_fixtures_dir):
        pptx_path = sld_similarity_fixtures_dir / "custom_titles.pptx"
        checker = SldSimilarity(str(pptx_path), goals="Задачи работы", conclusion="Выводы")
        
        result = checker.check()
        
        assert result.status is True

    def test_05_missing_conclusion_section(self, sld_similarity_fixtures_dir):
        pptx_path = sld_similarity_fixtures_dir / "missing_conclusion.pptx"
        checker = SldSimilarity(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False

    def test_06_boundary_value(self, sld_similarity_fixtures_dir):
        pptx_path = sld_similarity_fixtures_dir / "boundary_value.pptx"
        checker = SldSimilarity(str(pptx_path), min_percent=50)
        
        result = checker.check()
        
        assert result.status is True