import pytest
from app.main.checks.presentation_checks.find_tasks import FindTasks
from helpers import make_file_info, verdict_str


class TestFindTasks:

    def _make_checker(self, path, **kwargs):
        return FindTasks(make_file_info(str(path)), **kwargs)

    def test_01_all_tasks_found(self, find_tasks_fixtures_dir):
        checker = self._make_checker(find_tasks_fixtures_dir / "all_tasks_found.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Все задачи найдены на слайдах"

    def test_02_goal_slide_not_found(self, find_tasks_fixtures_dir):
        checker = self._make_checker(find_tasks_fixtures_dir / "no_goal_slide.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert verdict_str(result) == 'Слайд "Задачи" не найден'

    def test_03_below_threshold(self, find_tasks_fixtures_dir):
        checker = self._make_checker(find_tasks_fixtures_dir / "below_threshold.pptx")
        result = checker.check()
        assert result['score'] == pytest.approx(0.4)
        assert "не найдены" in verdict_str(result) or "Не найдены" in verdict_str(result)

    def test_04_above_threshold(self, find_tasks_fixtures_dir):
        checker = self._make_checker(find_tasks_fixtures_dir / "above_threshold.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Все задачи найдены на слайдах"

    def test_05_boundary_value(self, find_tasks_fixtures_dir):
        checker = self._make_checker(find_tasks_fixtures_dir / "boundary_value.pptx")
        result = checker.check()
        assert result['score'] == pytest.approx(0.5)
        assert "не найдены" in verdict_str(result) or "Не найдены" in verdict_str(result)

    def test_06_custom_threshold(self, find_tasks_fixtures_dir):
        checker = self._make_checker(find_tasks_fixtures_dir / "custom_threshold.pptx", min_percent=70)
        result = checker.check()
        assert result['score'] == pytest.approx(0.8)
        assert "найдены" in verdict_str(result) or "Найдены" in verdict_str(result)