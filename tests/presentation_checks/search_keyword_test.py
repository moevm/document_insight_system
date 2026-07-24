import pytest
from unittest.mock import Mock
from app.main.checks.presentation_checks.search_keyword import SearchKeyWord


class TestSearchKeyword:
    def test_sk1(self):
        mock_presentation = Mock()
        mock_presentation.get_text_from_slides.return_value = [
            "Текст слайда 1",
            "Текст слайда 2",
            "Актуальность темы",
            "Текст слайда 4",
            "Текст слайда 5"
        ]

        check = SearchKeyWord(file=mock_presentation, key_slide=["Актуальность"])

        result = check.check()

        assert result.score == True
        assert "3" in result.message

    def test_sk2(self):
        mock_presentation = Mock()
        mock_presentation.get_text_from_slides.return_value = [
            "Текст слайда 1",
            "Текст слайда 2",
            "Текст слайда 3",
            "Текст слайда 4",
            "Текст слайда 5"
        ]

        check = SearchKeyWord(file=mock_presentation, key_slide=["Актуальность"])

        result = check.check()

        assert result.score == False
        assert "Слайд не найден" in result.message