import pytest
from app.main.checks.presentation_checks.task_tracker import TaskTracker
from helpers import make_file_info, verdict_str


class TestTaskTracker:

    def _make_checker(self, path, **kwargs):
        return TaskTracker(make_file_info(str(path)), **kwargs)

    def test_01_tasks_formulated_correctly(self, task_tracker_fixtures_dir):
        checker = self._make_checker(task_tracker_fixtures_dir / "correct_tasks.pptx")
        result = checker.check()
        assert result['score'] == 1.0
        assert verdict_str(result) == "Задачи сформулированы корректно!"

    def test_02_forbidden_words_detected(self, task_tracker_fixtures_dir):
        checker = self._make_checker(task_tracker_fixtures_dir / "forbidden_words.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "не должны содержать слова" in verdict_str(result)
        assert "решить" in verdict_str(result)
        assert "описать" in verdict_str(result)
        assert "доделать" in verdict_str(result)

    def test_03_goal_and_tasks_slide_missing(self, task_tracker_fixtures_dir):
        checker = self._make_checker(task_tracker_fixtures_dir / "missing_slide.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert verdict_str(result) == 'Слайда "Цель и задачи" не существует'

    def test_04_custom_deny_list(self, task_tracker_fixtures_dir):
        checker = self._make_checker(task_tracker_fixtures_dir / "custom_deny_list.pptx", deny_list=['создать', 'реализовать'])
        result = checker.check()
        assert result['score'] == 0.0
        assert "не должны содержать слова" in verdict_str(result)
        assert "создать" in verdict_str(result)
        assert "реализовать" in verdict_str(result)

    def test_05_custom_section_title(self, task_tracker_fixtures_dir):
        checker = self._make_checker(task_tracker_fixtures_dir / "custom_title.pptx", goal_and_tasks="Задачи работы")
        result = checker.check()
        assert result['score'] == 0.0
        assert "не должны содержать слова" in verdict_str(result)
        assert "решить" in verdict_str(result)

    def test_06_stemming_and_normalization(self, task_tracker_fixtures_dir):
        checker = self._make_checker(task_tracker_fixtures_dir / "different_forms.pptx")
        result = checker.check()
        assert result['score'] == 0.0
        assert "не должны содержать слова" in verdict_str(result)
        assert "доделать" in verdict_str(result)
        assert "решить" in verdict_str(result)
        assert "описать" in verdict_str(result)