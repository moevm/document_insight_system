import pytest
from unittest.mock import Mock
from app.main.checks.presentation_checks.find_theme_in_pres import FindThemeInPres


class TestFindThemeInPres:
    def test_fitip1(self):
        mock_presentation = Mock()
        mock_presentation.theme = "Искусственный интеллект в медицине"
        mock_presentation.get_text_from_slides.return_value = [
            "Искусственный интеллект помогает в медицине",
            "Медицинские применения ИИ",
            "Будущее медицины с ИИ"
        ]
        mock_presentation.get_titles.return_value = [
            "Титульный слайд",
            "Введение",
            "Содержание",
            "Заключение"
        ]

        check = FindThemeInPres(file=mock_presentation)

        result = check.check()

        assert result.score == True
        assert "100 %" in result.message

    def test_fitip2(self):
        mock_presentation = Mock()
        mock_presentation.theme = "Искусственный интеллект в медицине"
        mock_presentation.get_text_from_slides.return_value = [
            "Другой текст",
            "Не содержит ключевых слов",
            "Просто текст"
        ]
        mock_presentation.get_titles.return_value = [
            "Титульный слайд",
            "Введение",
            "Содержание",
            "Заключение"
        ]

        check = FindThemeInPres(file=mock_presentation)

        result = check.check()

        assert result.score == False
        assert "Не пройдена!" in result.message

    def test_fitip3(self):
        mock_presentation = Mock()
        mock_presentation.theme = "Искусственный интеллект"
        mock_presentation.get_text_from_slides.return_value = [
            "Текст без темы",
            "Искусственный интеллект упоминается только в заключении"
        ]
        mock_presentation.get_titles.return_value = [
            "Титульный слайд",
            "Заключение"
        ]

        check = FindThemeInPres(file=mock_presentation)

        result = check.check()

        assert result.score == False
        assert "Не пройдена!" in result.message