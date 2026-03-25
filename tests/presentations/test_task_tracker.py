import pytest
from app.main.checks.presentation_checks.task_tracker import TaskTracker


class TestTaskTracker:

    def test_01_tasks_formulated_correctly(self, task_tracker_fixtures_dir):
        pptx_path = task_tracker_fixtures_dir / "correct_tasks.pptx"
        checker = TaskTracker(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is True
        assert result.result_str == "Задачи сформулированы корректно!"

    def test_02_forbidden_words_detected(self, task_tracker_fixtures_dir):
        pptx_path = task_tracker_fixtures_dir / "forbidden_words.pptx"
        checker = TaskTracker(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "не должны содержать слова" in result.result_str
        assert "решить" in result.result_str
        assert "описать" in result.result_str
        assert "доделать" in result.result_str

    def test_03_goal_and_tasks_slide_missing(self, task_tracker_fixtures_dir):
        pptx_path = task_tracker_fixtures_dir / "missing_slide.pptx"
        checker = TaskTracker(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert result.result_str == 'Слайда "Цель и задачи" не существует'

    def test_04_custom_deny_list(self, task_tracker_fixtures_dir):
        pptx_path = task_tracker_fixtures_dir / "custom_deny_list.pptx"
        deny_list = ['создать', 'реализовать']
        checker = TaskTracker(str(pptx_path), deny_list=deny_list)
        
        result = checker.check()
        
        assert result.status is False
        assert "не должны содержать слова" in result.result_str
        assert "создать" in result.result_str
        assert "реализовать" in result.result_str

    def test_05_custom_section_title(self, task_tracker_fixtures_dir):
        pptx_path = task_tracker_fixtures_dir / "custom_title.pptx"
        checker = TaskTracker(str(pptx_path), goal_and_tasks="Задачи работы")
        
        result = checker.check()
        
        assert result.status is False
        assert "не должны содержать слова" in result.result_str
        assert "решить" in result.result_str

    def test_06_stemming_and_normalization(self, task_tracker_fixtures_dir):
        pptx_path = task_tracker_fixtures_dir / "different_forms.pptx"
        checker = TaskTracker(str(pptx_path))
        
        result = checker.check()
        
        assert result.status is False
        assert "не должны содержать слова" in result.result_str
        assert "доделать" in result.result_str
        assert "решить" in result.result_str
        assert "описать" in result.result_str