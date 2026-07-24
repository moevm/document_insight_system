import pytest
from unittest.mock import Mock
from app.main.checks.presentation_checks.image_share import PresImageShareCheck


class TestImageShare:
    def test_is1(self):
        mock_presentation = Mock()
        mock_presentation.slides = [Mock() for _ in range(10)]
        for slide in mock_presentation.slides:
            slide.has_image = True

        check = PresImageShareCheck(file=mock_presentation, limit=0.9)

        result = check.check()

        assert result.score == False
        assert "1.0" in result.message
        assert "0.9" in result.message

    def test_is2(self):
        mock_presentation = Mock()
        mock_presentation.slides = [Mock() for _ in range(10)]
        for i in range(9):
            mock_presentation.slides[i].has_image = True
        mock_presentation.slides[9].has_image = False

        check = PresImageShareCheck(file=mock_presentation, limit=0.9)

        result = check.check()

        assert result.score == True
        assert result.message == 'Пройдена!'

    def test_is3(self):
        mock_presentation = Mock()
        mock_presentation.slides = [Mock()]
        mock_presentation.slides[0].has_image = True

        check = PresImageShareCheck(file=mock_presentation, limit=0.9)

        result = check.check()

        assert result.score == False
        assert "1.0" in result.message

    def test_is4(self):
        mock_presentation = Mock()
        mock_presentation.slides = [Mock() for _ in range(10)]
        for slide in mock_presentation.slides:
            slide.has_image = False

        check = PresImageShareCheck(file=mock_presentation, limit=0.9)

        result = check.check()

        assert result.score == True
        assert result.message == 'Пройдена!'