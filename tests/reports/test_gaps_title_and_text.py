from unittest.mock import MagicMock

from app.main.checks.report_checks.gaps_title_and_text import ReportGapsBetweenTitleAndTextCheck


def make_header(header_name="text_header", header_style="heading 1", header_text="text_in_header"):
    return {
        "style": header_style,
        "text": header_name,
        "child": [{"text": header_text}],
    }


def make_checker(headers=None, page_counter=5, text_on_page=None):
    obj = ReportGapsBetweenTitleAndTextCheck.__new__(ReportGapsBetweenTitleAndTextCheck)

    obj.file_type = {"type": "report", "report_type": "VKR"}

    obj.file = MagicMock()
    obj.file.make_chapters.return_value = headers or []
    obj.file.page_counter.return_value = page_counter
    obj.file.pdf_file = MagicMock()
    obj.file.pdf_file.text_on_page = text_on_page or {}

    return obj


class TestNoHeaders:
    def test_no_headers(self):
        checker = make_checker(headers=[])
        result = checker.check()

        assert result["score"] == 0.0
        assert "Не найдено ни одного заголовка" in str(result["verdict"])

    def test_headers_without_heading_style(self):
        headers = [make_header(header_style="text")]
        text_on_page = {
            1: "ВВЕДЕНИЕ Цель работы ...",
            2: "Анализ производительности показал ...",
            3: "ЗАКЛЮЧЕНИЕ Итоги работы ...",
        }
        checker = make_checker(headers=headers, page_counter=3, text_on_page=text_on_page)
        result = checker.check()

        assert result["score"] == 1.0


class TestValidDocument:
    def test_header_and_text_on_same_page(self):
        headers = [make_header(header_name="ВВЕДЕНИЕ", header_text="Цель работы является прорбаотка краевых случаев")]
        text_on_page = {1: "ВВЕДЕНИЕ Цель работы является прорбаотка краевых случаев"}
        checker = make_checker(headers=headers, page_counter=1, text_on_page=text_on_page)
        result = checker.check()

        assert result["score"] == 1.0

    def test_multiple_headers_all_ok(self):
        headers = [
            make_header(header_name="ВВЕДЕНИЕ", header_text="Цель работы"),
            make_header(header_name="ЗАКЛЮЧЕНИЕ", header_text="Итоги работы"),
        ]
        text_on_page = {
            1: "ВВЕДЕНИЕ Цель работы ...",
            2: "Анализ производительности показал ...",
            3: "ЗАКЛЮЧЕНИЕ Итоги работы ...",
        }
        checker = make_checker(
            headers=headers,
            page_counter=3,
            text_on_page=text_on_page,
        )
        result = checker.check()

        assert result["score"] == 1.0


class TestHangingHeaders:
    def test_header_on_page_without_text(self):
        headers = [make_header(header_name="ВВЕДЕНИЕ", header_text="Цель работы")]
        text_on_page = {
            1: "ВВЕДЕНИЕ",
            2: "Цель работы ...",
        }
        checker = make_checker(
            headers=headers,
            page_counter=2,
            text_on_page=text_on_page,
        )
        result = checker.check()

        assert result["score"] == 0.0
        assert "висячие заголовки" in str(result["verdict"])

    def test_two_hanging_headers(self):
        headers = [
            make_header(header_name="ВВЕДЕНИЕ", header_text="Цель работы"),
            make_header(header_name="ЗАКЛЮЧЕНИЕ", header_text="Итоги работы"),
        ]
        text_on_page = {
            1: "ВВЕДЕНИЕ",
            2: "Цель работы ...",
            3: "Анализ производительности показал ...",
            4: "ЗАКЛЮЧЕНИЕ",
            5: "Анализ производительности показал ...",
            6: "Итоги работы ...",
        }
        checker = make_checker(
            headers=headers,
            page_counter=6,
            text_on_page=text_on_page,
        )
        result = checker.check()

        assert result["score"] == 0.0
        assert "ВВЕДЕНИЕ" in str(result["verdict"])
        assert "ЗАКЛЮЧЕНИЕ" in str(result["verdict"])

    def test_empty_text_on_page(self):
        headers = [make_header(header_name="ВВЕДЕНИЕ", header_text="Цель работы")]
        text_on_page = {1: ""}
        checker = make_checker(
            headers=headers,
            page_counter=1,
            text_on_page=text_on_page,
        )
        result = checker.check()

        assert result["score"] == 1.0
