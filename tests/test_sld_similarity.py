import pytest
from app.main.checks.presentation_checks.sld_similarity import SldSimilarity
from helpers import make_file_info, verdict_str


class TestSldSimilarity:

    def _make_checker(self, path, **kwargs):
        return SldSimilarity(make_file_info(str(path)), **kwargs)

    def test_01_full_compliance(self, sld_similarity_fixtures_dir):
        checker = self._make_checker(sld_similarity_fixtures_dir / "full_compliance.pptx")
        result = checker.check()
        assert result['score'] == 1.0

    def test_02_partial_compliance_above_threshold(self, sld_similarity_fixtures_dir):
        checker = self._make_checker(sld_similarity_fixtures_dir / "partial_compliance.pptx", min_percent=70)
        result = checker.check()
        assert result['score'] == 1.0

    def test_03_compliance_below_threshold(self, sld_similarity_fixtures_dir):
        checker = self._make_checker(sld_similarity_fixtures_dir / "low_compliance.pptx")
        result = checker.check()
        assert result['score'] == 0.0

    def test_04_custom_section_titles(self, sld_similarity_fixtures_dir):
        checker = self._make_checker(sld_similarity_fixtures_dir / "custom_titles.pptx", goals="Задачи работы", conclusion="Выводы")
        result = checker.check()
        assert result['score'] == 1.0

    def test_05_missing_conclusion_section(self, sld_similarity_fixtures_dir):
        checker = self._make_checker(sld_similarity_fixtures_dir / "missing_conclusion.pptx")
        result = checker.check()
        assert result['score'] == 0.0

    def test_06_boundary_value(self, sld_similarity_fixtures_dir):
        checker = self._make_checker(sld_similarity_fixtures_dir / "boundary_value.pptx", min_percent=50)
        result = checker.check()
        assert result['score'] == 1.0