from unittest.mock import MagicMock

import pytest

from app.main.checks.report_checks.intervals_between_paragraphs import ReportIntervalsParagraphsCheck


def make_paragraph(text, style="normal", line_spacing=1.5, space_before=0, space_after=0):
    p = MagicMock()
    p.paragraph_text = text
    p.paragraph_style_name = style
    p.paragraph_line_spacing = line_spacing
    p.paragraph_space_before = space_before
    p.paragraph_space_after = space_after
    return p


def make_checker(
    paragraphs=None,
    params=None,
):
    obj = ReportIntervalsParagraphsCheck.__new__(ReportIntervalsParagraphsCheck)

    default_params = {
        'line_spacing': 1.5,
        'space_before': 0,
        'space_after': 0,
        'max_problematic_paragraphs': 10,
    }

    p = {**default_params, **(params or {})}

    obj.max_line_spacing = p['line_spacing']
    obj.space_before = p['space_before']
    obj.space_after = p['space_after']
    obj.max_problematic_paragraphs = p['max_problematic_paragraphs']

    obj.file = MagicMock()
    obj.file.paragraphs = paragraphs or []

    return obj


class TestValidDocument:
    def test_all_correct(self):
        paragraphs = [
            make_paragraph("Первый абзац"),
            make_paragraph("Второй абзац"),
            make_paragraph("Третий абзац"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 1.0

    def test_empty_document(self):
        checker = make_checker(paragraphs=[])
        result = checker.check()

        assert result["score"] == 1.0

    def test_headings_ignored(self):
        paragraphs = [
            make_paragraph("ВВЕДЕНИЕ", style="heading 1", line_spacing=2.0),
            make_paragraph("ПОСТАНОВКА ЗАДАЧИ", line_spacing=1.5),
            make_paragraph("ЗАКЛЮЧЕНИЕ", style="heading 2", space_before=10),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 1.0


class TestProblems:
    def test_wrong_line_spacing(self):
        paragraphs = [
            make_paragraph("ВВЕДЕНИЕ"),
            make_paragraph("ВВЕДЕНИЕ", line_spacing=2.0),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert 0 < result["score"] < 1.0

    def test_wrong_space_before(self):
        paragraphs = [
            make_paragraph("Плохой абзац", space_before=12),
            make_paragraph("Плохой абзац", space_before=12),
            make_paragraph("Плохой абзац", space_before=12),
            make_paragraph("Хороший абзац"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert 0 < result["score"] < 1.0

    def test_wrong_space_after(self):
        paragraphs = [
            make_paragraph("Плохой", space_after=6),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert 0 < result["score"] < 1.0

    def test_multiple_issues_in_one_paragraph(self):
        paragraphs = [
            make_paragraph("Плохой абзац", line_spacing=2.0, space_before=12, space_after=6),
            make_paragraph("Хороший абзац"),
            make_paragraph("Хороший абзац"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == pytest.approx(0.9)

    def test_all_paragraphs_bad(self):
        paragraphs = [
            make_paragraph("Плохой абзац", line_spacing=2.0),
            make_paragraph("Плохой абзац", line_spacing=2.0, space_before=12),
            make_paragraph("Плохой абзац", space_before=12),
            make_paragraph("Плохой абзац", line_spacing=2.0, space_after=6),
            make_paragraph("Плохой абзац", line_spacing=2.0, space_before=12, space_after=6),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 0.5


class TestScore:
    def test_score_at_threshold(self):
        paragraphs = [make_paragraph(f"Плохой абзац {i}", line_spacing=2.0) for i in range(10)]
        checker = make_checker(paragraphs=paragraphs, params={"max_problematic_paragraphs": 10})
        result = checker.check()

        assert result["score"] == 0.0

    def test_score_above_threshold(self):
        paragraphs = [make_paragraph(f"Плохой абзац {i}", line_spacing=2.0) for i in range(20)]
        checker = make_checker(paragraphs=paragraphs, params={"max_problematic_paragraphs": 10})
        result = checker.check()

        assert result["score"] == 0.0

    def test_score_proportional(self):
        paragraphs = [
            make_paragraph("Плохой абзац", line_spacing=2.0),
            make_paragraph("Плохой абзац", line_spacing=2.0),
            make_paragraph("Хороший абзац"),
            make_paragraph("Хороший абзац"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == pytest.approx(0.8)


class TestParams:
    def test_custom_line_spacing(self):
        paragraphs = [
            make_paragraph("Абзац line_spacing 1.5", line_spacing=1.5),
        ]
        checker = make_checker(paragraphs=paragraphs, params={"line_spacing": 2.0})
        result = checker.check()

        assert result["score"] == 0.9

    def test_custom_space_before(self):
        paragraphs = [
            make_paragraph("Абзац space_before 12", space_before=12),
        ]
        checker = make_checker(paragraphs=paragraphs, params={"space_before": 12})
        result = checker.check()

        assert result["score"] == 1.0

    def test_custom_params_match(self):
        paragraphs = [
            make_paragraph("Введение", line_spacing=2.0, space_before=12, space_after=6),
        ]
        checker = make_checker(
            paragraphs=paragraphs,
            params={
                "line_spacing": 2.0,
                "space_before": 12,
                "space_after": 6,
            },
        )
        result = checker.check()

        assert result["score"] == 1.0


class TestEdgeCases:
    def test_none_values_ignored(self):
        paragraphs = [make_paragraph("None", line_spacing=None, space_before=None, space_after=None)]

        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 1.0

    def test_paragraph_without_text_skipped(self):
        paragraphs = [
            make_paragraph("", line_spacing=2.0),
            make_paragraph("Введение"),
        ]
        checker = make_checker(paragraphs=paragraphs)
        result = checker.check()

        assert result["score"] == 1.0
