import pytest
from unittest.mock import Mock
from app.main.checks.presentation_checks.sld_num import SldNumCheck


class TestSldNum:
    def test_sn1(self):
        mock_presentation = Mock()
        mock_presentation.slides = [Mock() for _ in range(15)]

        check = SldNumCheck(
            file=mock_presentation,
            slides_number=[10, 20],
            detect_additional=False
        )

        result = check.check()

        assert result.score == True
        assert "допустимых границах" in result.message

    def test_sn2(self):
        mock_presentation = Mock()
        mock_presentation.slides = [Mock() for _ in range(25)]

        check = SldNumCheck(
            file=mock_presentation,
            slides_number=[10, 20],
            detect_additional=False
        )

        result = check.check()

        assert result.score == False
        assert "25" in result.message
        assert "превышает" in result.message