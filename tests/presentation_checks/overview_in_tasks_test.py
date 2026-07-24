import pytest
from unittest.mock import Mock
from app.main.checks.presentation_checks.overview_in_tasks import OverviewInTasks


class TestOverviewInTasks:
    def test_oit1(self):
        mock_presentation = Mock()
        tasks_slide = Mock()
        tasks_slide.get_text.return_value = "1. Обзор литературы\n2. Анализ данных"
        mock_presentation.find_slide_by_title.return_value = tasks_slide

        check = OverviewInTasks(file=mock_presentation)

        result = check.check()

        assert result.score == True
        assert 'Пройдена!' in result.message

    def test_oit2(self):
        mock_presentation = Mock()
        tasks_slide = Mock()
        tasks_slide.get_text.return_value = "1. Анализ существующих решений"
        mock_presentation.find_slide_by_title.return_value = tasks_slide

        check = OverviewInTasks(file=mock_presentation)

        result = check.check()

        assert result.score == True
        assert 'Пройдена!' in result.message

    def test_oit3(self):
        mock_presentation = Mock()
        tasks_slide = Mock()
        tasks_slide.get_text.return_value = "1. Исследование\n2. Разработка"
        mock_presentation.find_slide_by_title.return_value = tasks_slide

        check = OverviewInTasks(file=mock_presentation)

        result = check.check()

        assert result.score == False
        assert 'обзора' in result.message or 'анализа' in result.message