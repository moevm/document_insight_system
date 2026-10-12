from unittest.mock import MagicMock

from app.main.checks.report_checks.structure_check import ReportStructureCheck
from app.main.checks.report_checks.style_check_settings import StyleCheckSettings


def make_paragraph(text, style="normal"):
    p = MagicMock()
    p.paragraph_text = text
    p.paragraph_style_name = style
    return p


def make_checker(
    paragraphs=None, chapters=None, page_count=10, headers_page=1, main_headers="Задание на ВКР", file_type=None
):
    obj = ReportStructureCheck.__new__(ReportStructureCheck)
    obj.pdf_id = "pdf_id"
    obj.file_type = file_type or {"type": "report", "report_type": "VKR"}
    obj.required_sections = StyleCheckSettings.REQUIRED_SECTIONS_BEFORE_INTRO
    obj.headers_page = headers_page
    obj.headers = []
    obj.patterns = []
    obj.main_heading_style = "heading 2"
    obj.config = "VKR_HEADERS"

    obj.file = MagicMock()
    obj.file.paragraphs = paragraphs or []
    obj.file.page_counter.return_value = page_count
    obj.file.make_chapters.return_value = chapters or []
    obj.file.find_header_page.return_value = headers_page
    obj.file.show_chapters.return_value = "<br>"
    obj.file.get_main_headers.return_value = main_headers

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


class TestCheckNeededHeaders:
    def test_too_few_pages(self):
        checker = make_checker(page_count=3)
        result, message = checker.check_needed_headers()

        assert result is False
        assert "В отчете недостаточно страниц." in message

    def test_all_headers_found(self):
        chapters = [
            {"text": "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", "style": "heading 2"},
            {"text": "ВВЕДЕНИЕ", "style": "heading 2"},
            {"text": "ЗАКЛЮЧЕНИЕ", "style": "heading 2"},
            {"text": "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "style": "heading 2"},
        ]
        checker = make_checker(chapters=chapters)

        checker.patterns = [
            "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ",
            "ВВЕДЕНИЕ",
            "ЗАКЛЮЧЕНИЕ",
            "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        ]
        result, message = checker.check_needed_headers()
        assert result is True

    def test_some_headers_missing(self):
        chapters = [
            {"text": "ВВЕДЕНИЕ", "style": "heading 2"},
        ]
        checker = make_checker(chapters=chapters)

        checker.patterns = [
            "ВВЕДЕНИЕ",
            "ЗАКЛЮЧЕНИЕ",
        ]

        result, message = checker.check_needed_headers()
        assert result is False
        assert "ЗАКЛЮЧЕНИЕ" in message

    def test_no_headers_found(self):

        checker = make_checker(chapters=[])
        checker.patterns = ["ВВЕДЕНИЕ"]
        result, message = checker.check_needed_headers()

        assert result is False

    def test_empty_patterns(self):
        checker = make_checker()
        checker.patterns = []
        result, message = checker.check_needed_headers()

        assert result is False
