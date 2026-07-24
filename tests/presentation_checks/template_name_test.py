import pytest
from unittest.mock import Mock, patch
from app.main.checks.presentation_checks.template_name import PresTemplateNameCheck


class TestTemplateName:
    def test_tn1(self):
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.year = 2026

            mock_presentation = Mock()
            mock_presentation.name = "2026ВКР123456ИВАНОВ_презентация.pptx"

            check = PresTemplateNameCheck(file=mock_presentation)

            result = check.check()

            assert result.score == True
            assert result.message == 'Пройдена!'

    def test_tn2(self):
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.year = 2026

            mock_presentation = Mock()
            mock_presentation.name = "2025ВКР123456ИВАНОВ_презентация.pptx"

            check = PresTemplateNameCheck(file=mock_presentation)

            result = check.check()

            assert result.score == False
            assert "не соответствует шаблону" in result.message