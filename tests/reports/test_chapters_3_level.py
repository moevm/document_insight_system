from unittest.mock import MagicMock

import pytest

from app.main.checks.report_checks.check_chapters_3_level import ReportСhaptersLevel3ContentCheck


def make_paragraph(text, style="normal"):
    p = MagicMock()
    p.paragraph_text = text
    p.paragraph_style_name = style
    return p


def make_checker(paragraphs=None, forbidden_depth=3):
    obj = ReportСhaptersLevel3ContentCheck.__new__(ReportСhaptersLevel3ContentCheck)
    obj.forbidden_depth = forbidden_depth
    obj.end_marker = "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ"
    obj.file = MagicMock()
    obj.file.paragraphs = paragraphs or []
    return obj


class TestForbiddenLevel:
    @pytest.mark.parametrize(
        "line, expected",
        [
            ("1. ВВЕДЕНИЕ", False),
            ("2. ЗАКЛЮЧЕНИЕ", False),
            ("1 ВВЕДЕНИЕ", False),
            ("1.1. ЗАКЛЮЧЕНИЕ", False),
            ("1.1 ЗАКЛЮЧЕНИЕ", False),
            ("2.3. ВВЕДЕНИЕ ВВЕДЕНИЕ", False),
            ("1.1.1. ВВЕДЕНИЕ", True),
            ("1.1.1 ВВЕДЕНИЕ", True),
            ("2.3.1. ВВЕДЕНИЕ", True),
            ("1.1.1.1. ВВЕДЕНИЕ", True),
            ("1.1.1.1  ", True),
            ("ВВЕДЕНИЕ", False),
            ("", False),
        ],
    )
    def test_is_forbidden_depth_3(self, line, expected):
        checker = make_checker(forbidden_depth=3)
        assert checker._is_forbidden_depth(line) is expected

    @pytest.mark.parametrize(
        "line, expected",
        [
            ("1. ВВЕДЕНИЕ", False),
            ("1.1. ЗАКЛЮЧЕНИЕ", True),
            ("1.1.1.", True),
        ],
    )
    def test_is_forbidden_depth_2(self, line, expected):
        checker = make_checker(forbidden_depth=2)
        assert checker._is_forbidden_depth(line) is expected

    @pytest.mark.parametrize(
        "line, expected",
        [
            ("1. ВВЕДЕНИЕ", False),
            ("1.1. ЗАКЛЮЧЕНИЕ", False),
            ("1.1.1. ЗАКЛЮЧЕНИЕ", False),
            ("1.1.1.1.", True),
        ],
    )
    def test_is_forbidden_depth_4(self, line, expected):
        checker = make_checker(forbidden_depth=4)
        assert checker._is_forbidden_depth(line) is expected


class TestCheck:
    def test_ok_content(self):
        paragraphs = [
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("1. ПОСТАНОВКА ЗАДАЧИ"),
            make_paragraph("1.1. РЕЗУЛЬТАТЫ"),
            make_paragraph("2. ЗАКЛЮЧЕНИЕ"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 1"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 1.0

    def test_content_with_deep_item(self):
        paragraphs = [
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("1.1.1. ПОСТАНОВКА ЗАДАЧИ"),
            make_paragraph("ЗАКЛЮЧЕНИЕ", style="heading 1"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 0.0
        assert "пунктов глубже" in str(result["verdict"])
        assert "глубина превышает 2" in str(result["verdict"])
        assert "{self.forbidden_depth" not in str(result["verdict"])

    def test_no_content_section(self):
        paragraphs = [
            make_paragraph("ВВЕДЕНИЕ"),
            make_paragraph("1.1.1. ЗАКЛЮЧЕНИЕ"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 0.0
        assert "Не найдено раздела" in str(result["verdict"])

    def test_lowercase_content(self):
        paragraphs = [
            make_paragraph("содержание"),
            make_paragraph("1.1.1. ЗАКЛЮЧЕНИЕ"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 1"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 0.0

    def test_content_ends_by_any_heading(self):
        paragraphs = [
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("1.1. ЗАКЛЮЧЕНИЕ"),
            make_paragraph("ВВЕДЕНИЕ", style="heading 1"),
            make_paragraph("1.1.1. ЗАКЛЮЧЕНИЕ"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 1.0

    def test_no_content_end(self):
        paragraphs = [
            make_paragraph("СОДЕРЖАНИЕ"),
            make_paragraph("1.1. Анализ"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 0.0
        assert "Не найден конец раздела" in str(result["verdict"])

    def test_empty_paragraphs(self):
        checker = make_checker(paragraphs=[])
        result = checker.check()

        assert result["score"] == 0.0
