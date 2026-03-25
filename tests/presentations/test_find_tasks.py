import pytest
from app.main.checks.presentation_checks.find_tasks import FindTasks


class TestFindTasks:

    def test_01_all_tasks_found(self, find_tasks_fixtures_dir):
        pptx_path = find_tasks_fixtures_dir / "all_tasks_found.pptx"
        checker = FindTasks(str(pptx_path))
        
        result = checker.check()
        
        assert result.status == 1
        assert result.result_str == "Все задачи найдены на слайдах"

    def test_02_goal_slide_not_found(self, find_tasks_fixtures_dir):
        pptx_path = find_tasks_fixtures_dir / "no_goal_slide.pptx"
        checker = FindTasks(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert result.result_str == 'Слайд "Задачи" не найден'

    def test_03_below_threshold(self, find_tasks_fixtures_dir):
        pptx_path = find_tasks_fixtures_dir / "below_threshold.pptx"
        checker = FindTasks(str(pptx_path))
        
        result = checker.check()
        
        assert result.status == 0.4
        assert "не найдены" in result.result_str or "Не найдены" in result.result_str

    def test_04_above_threshold(self, find_tasks_fixtures_dir):
        pptx_path = find_tasks_fixtures_dir / "above_threshold.pptx"
        checker = FindTasks(str(pptx_path))
        
        result = checker.check()
        
        assert result.status == 1
        assert result.result_str == "Все задачи найдены на слайдах"

    def test_05_boundary_value(self, find_tasks_fixtures_dir):
        pptx_path = find_tasks_fixtures_dir / "boundary_value.pptx"
        checker = FindTasks(str(pptx_path))
        
        result = checker.check()
        
        assert result.status == 0.5
        assert "не найдены" in result.result_str or "Не найдены" in result.result_str

    def test_06_custom_threshold(self, find_tasks_fixtures_dir):
        pptx_path = find_tasks_fixtures_dir / "custom_threshold.pptx"
        checker = FindTasks(str(pptx_path), min_percent=70)
        
        result = checker.check()
        
        assert result.status == 0.8
        assert "найдены" in result.result_str or "Найдены" in result.result_str