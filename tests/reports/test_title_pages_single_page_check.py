from unittest.mock import MagicMock

import pytest

from app.main.checks.report_checks.title_pages_single_page_check import TitlePagesSinglePage
from tests.util.report_file_utils import create_report_file_info

TITLE = "САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ ЭЛЕКТРОТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ\n«ЛЭТИ»"
TASK = "ЗАДАНИЕ\nна выпускную квалификационную работу"
PLAN = "КАЛЕНДАРНЫЙ ПЛАН\nвыполнения выпускной квалификационной работы"
REFERAT = "РЕФЕРАТ\nПояснительная записка содержит 60 страниц."
ABSTRACT = "ABSTRACT\nThe explanatory note contains 60 pages."
CONTENTS = "СОДЕРЖАНИЕ\nВведение 6"
INTRO = "ВВЕДЕНИЕ\nТекст введения."
CONTINUATION = "продолжение раздела\nТекст."
TASK_NAME = '"Задание на выпускную квалификационную работу"'
FILLER_PAGES = 8


class TestTitlePagesSinglePage:
    @pytest.fixture(autouse=True)
    def no_conversion(self, monkeypatch):
        from main.reports.pdf_document import pdf_document_manager

        monkeypatch.setattr(pdf_document_manager, "convert_to", lambda *args, **kwargs: None)

    def _make_checker(self, reports_fixture_dir, fixture, pages):
        file_info = create_report_file_info(reports_fixture_dir / "title_pages_single_page" / fixture)
        texts = list(pages) + ["Основной текст работы."] * FILLER_PAGES
        pages_text = {num: text for num, text in enumerate(texts, start=1)}
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value=pages_text)
        file_info['file'].pdf_file.text_on_page = pages_text
        return TitlePagesSinglePage(file_info)

    def _check(self, reports_fixture_dir, fixture, pages):
        return self._make_checker(reports_fixture_dir, fixture, pages).check()

    def test_01_all_sections_on_one_page(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir, "title_pages.docx", [TITLE, TASK, PLAN, REFERAT, ABSTRACT, CONTENTS, INTRO]
        )
        assert result["score"] == 1.0
        assert result["verdict"][0] == "Каждая титульная страница занимает не более одного листа."

    def test_02_task_on_two_pages(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir,
            "title_pages.docx",
            [TITLE, TASK, CONTINUATION, PLAN, REFERAT, ABSTRACT, CONTENTS, INTRO],
        )
        assert result["score"] == 0.0
        verdict = result["verdict"][0]
        assert verdict.startswith(f"{TASK_NAME} занимает более одной страницы")
        assert "#page=2" in verdict
        assert "#page=3" in verdict

    def test_03_task_on_three_pages_shows_full_range(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir,
            "title_pages.docx",
            [TITLE, TASK, CONTINUATION, CONTINUATION, PLAN, REFERAT, ABSTRACT, CONTENTS, INTRO],
        )
        assert result["score"] == 0.0
        verdict = result["verdict"][0]
        assert verdict.startswith(TASK_NAME)
        assert "#page=2" in verdict
        assert "#page=4" in verdict

    def test_04_text_overflows_onto_next_section_page(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir,
            "title_pages.docx",
            [TITLE, TASK, "слово\nКАЛЕНДАРНЫЙ ПЛАН", REFERAT, ABSTRACT, CONTENTS, INTRO],
        )
        assert result["score"] == 0.0
        verdict = result["verdict"][0]
        assert verdict.startswith(TASK_NAME)
        assert "#page=3" in verdict

    def test_05_title_on_two_pages(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir,
            "title_pages.docx",
            [TITLE, CONTINUATION, TASK, PLAN, REFERAT, ABSTRACT, CONTENTS, INTRO],
        )
        assert result["score"] == 0.0
        verdict = result["verdict"][0]
        assert verdict.startswith('"Титульный лист" занимает более одной страницы')
        assert "#page=1" in verdict
        assert "#page=2" in verdict

    def test_06_multiple_violations(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir,
            "title_pages.docx",
            [TITLE, TASK, CONTINUATION, PLAN, REFERAT, CONTINUATION, ABSTRACT, CONTENTS, INTRO],
        )
        assert result["score"] == 0.0
        violations = result["verdict"][0].split("<br>")
        assert len(violations) == 2
        assert violations[0].startswith(TASK_NAME)
        assert violations[1].startswith('"Реферат"')
        assert "#page=5" in violations[1]
        assert "#page=6" in violations[1]

    def test_07_missing_section_in_the_middle(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "title_pages.docx", [TITLE, TASK, REFERAT, ABSTRACT, CONTENTS, INTRO])
        assert result["score"] == 1.0

    def test_08_contents_on_several_pages(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir,
            "title_pages.docx",
            [TITLE, TASK, PLAN, REFERAT, ABSTRACT, CONTENTS, CONTINUATION, CONTINUATION, INTRO],
        )
        assert result["score"] == 1.0

    def test_09_no_contents_last_found_section_not_checked(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "title_pages.docx", [TITLE, TASK, PLAN, REFERAT, ABSTRACT, INTRO])
        assert result["score"] == 1.0

    def test_10_no_abstract_and_contents(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "title_pages.docx", [TITLE, TASK, PLAN, REFERAT, INTRO])
        assert result["score"] == 1.0
