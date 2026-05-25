import pytest
from app.main.checks.presentation_checks.further_dev import FurtherDev
from helpers import make_file_info, verdict_str


class TestFurtherDev:

    def _make_checker(self, path, **kwargs):
        return FurtherDev(make_file_info(str(path)), **kwargs)

    def test_01_further_dev_found(self, further_dev_fixtures_dir):
        checker = self._make_checker(further_dev_fixtures_dir / "further_dev_found.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Направления развития найдены"

    def test_02_conclusion_not_exists(self, further_dev_fixtures_dir):
        checker = self._make_checker(further_dev_fixtures_dir / "no_conclusion.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert verdict_str(result) == "Заключения не существует"

    def test_03_no_further_dev_in_conclusion(self, further_dev_fixtures_dir):
        checker = self._make_checker(further_dev_fixtures_dir / "no_further_dev.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "Направления развития не найдены" in verdict_str(result)

    def test_04_custom_conclusion_title(self, further_dev_fixtures_dir):
        checker = self._make_checker(further_dev_fixtures_dir / "custom_conclusion.pptx", conclusion="Выводы и перспективы")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Направления развития найдены"

    def test_05_indirect_indicators(self, further_dev_fixtures_dir):
        checker = self._make_checker(further_dev_fixtures_dir / "indirect_indicators.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Направления развития найдены"

    def test_06_different_formats(self, further_dev_fixtures_dir):
        # ⚠️ .ppt (старый бинарный формат) не поддерживается python-pptx — тест упадёт с ошибкой открытия файла
        checker_ppt = self._make_checker(further_dev_fixtures_dir / "further_dev_found.ppt")
        result_ppt = checker_ppt.check()
        assert result_ppt['score'] == 1.0
        assert verdict_str(result_ppt) == "Направления развития найдены"

        checker_odp = self._make_checker(further_dev_fixtures_dir / "further_dev_found.odp")
        result_odp = checker_odp.check()
        assert result_odp['score'] == 1.0
        assert verdict_str(result_odp) == "Направления развития найдены"