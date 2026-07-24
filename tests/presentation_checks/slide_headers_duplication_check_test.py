import pytest
from unittest.mock import Mock
from app.main.checks.presentation_checks.slide_headers_duplication_check import SlideHeadersDuplicationCheck


class TestSlideHeadersDuplication:
    def test_shdc1(self):
        mock_presentation = Mock()
        slides = []
        headers = ["Введение", "Актуальность", "Цели и задачи", "Методы", "Заключение"]
        for i, header in enumerate(headers):
            slide = Mock()
            slide.get_title.return_value = header
            slides.append(slide)
        mock_presentation.slides = slides

        check = SlideHeadersDuplicationCheck(file=mock_presentation)

        result = check.check()

        assert result.score == True
        assert result.message == 'Пройдена!'

    def test_shdc2(self):
        mock_presentation = Mock()
        slides = []
        headers = ["Введение", "Актуальность", "Методы", "Методы"]
        for i, header in enumerate(headers):
            slide = Mock()
            slide.get_title.return_value = header
            slides.append(slide)
        mock_presentation.slides = slides

        check = SlideHeadersDuplicationCheck(file=mock_presentation)

        result = check.check()

        assert result.score == False
        assert "Методы" in result.message
        assert "3,4" in result.message

    def test_shdc3(self):
        mock_presentation = Mock()
        slides = []
        headers = ["Введение", "Введение", "Методы", "Методы", "Методы", "Заключение"]
        for i, header in enumerate(headers):
            slide = Mock()
            slide.get_title.return_value = header
            slides.append(slide)
        mock_presentation.slides = slides

        check = SlideHeadersDuplicationCheck(file=mock_presentation)

        result = check.check()

        assert result.score == False
        assert "Введение" in result.message
        assert "Методы" in result.message
        assert "1,2" in result.message
        assert "3,4,5" in result.message