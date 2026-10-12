from unittest.mock import MagicMock

from app.main.checks.report_checks.structure_check import ReportStructureCheck
from app.main.checks.report_checks.style_check_settings import StyleCheckSettings


def make_paragraph(text, style="normal"):
    p = MagicMock()
    p.paragraph_text = text
    p.paragraph_style_name = style
    return p


def make_checker(paragraphs=None):
    obj = ReportStructureCheck.__new__(ReportStructureCheck)
    obj.required_sections = StyleCheckSettings.REQUIRED_SECTIONS_BEFORE_INTRO

    obj.file = MagicMock()
    obj.file.paragraphs = paragraphs or []

    return obj


class TestCheckSequenceSections:
    def test_all_sections_in_order(self):
        paragraphs = [
            make_paragraph("ЗАДАНИЕ"),
            make_paragraph("календарный план"),
            make_paragraph("РЕФЕРАТ"),
            make_paragraph("ABSTRACT"),
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", style="heading 2"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 2"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result, message = checker.check_sequence_sections()

        assert result is True

    def test_intro_missing(self):
        paragraphs = [
            make_paragraph("ЗАДАНИЕ"),
            make_paragraph("РЕФЕРАТ"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result, message = checker.check_sequence_sections()

        assert result is False
        assert "ВВЕДЕНИЕ" in message

    def test_wrong_order(self):
        paragraphs = [
            make_paragraph("РЕФЕРАТ"),
            make_paragraph("ЗАДАНИЕ"),
            make_paragraph("календарный план"),
            make_paragraph("ABSTRACT"),
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", style="heading 2"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 2"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result, message = checker.check_sequence_sections()

        assert result is False

    def test_missing_some_sections(self):
        paragraphs = [
            make_paragraph("ЗАДАНИЕ"),
            make_paragraph("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", style="heading 2"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 2"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result, message = checker.check_sequence_sections()

        assert result is False

    def test_intro_wrong_style(self):
        paragraphs = [
            make_paragraph("ЗАДАНИЕ"),
            make_paragraph("календарный план"),
            make_paragraph("РЕФЕРАТ"),
            make_paragraph("ABSTRACT"),
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", style="heading 2"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 3"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result, message = checker.check_sequence_sections()

        assert result is False
        assert "Раздел 'ВВЕДЕНИЕ' должен быть оформлен стилем 'Заголовок 2'" in message

    def test_definition_wrong_style(self):
        paragraphs = [
            make_paragraph("ЗАДАНИЕ"),
            make_paragraph("календарный план"),
            make_paragraph("РЕФЕРАТ"),
            make_paragraph("ABSTRACT"),
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", style="heading 3"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 2"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result, message = checker.check_sequence_sections()

        assert result is False
        assert "Раздел 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ' должен быть оформлен стилем 'Заголовок 2'" in message
