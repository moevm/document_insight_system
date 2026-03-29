from unittest.mock import MagicMock
import pytest
from app.main.checks.report_checks.sw_section_lit_reference import SWSectionLiteratureReferenceCheck

class TestSWSectionLiteratureReferenceCheck:

    @pytest.fixture
    def checker(self):
        mock_file_info = MagicMock()
        mock_file_info.get.return_value = MagicMock()
        checker = SWSectionLiteratureReferenceCheck(mock_file_info, "SW_KEY_QUESTIONS_SECTIONS")
        return checker

    def test_01_valid_references_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_lit_ref" / "valid.docx"
        checker = SWSectionLiteratureReferenceCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Проверка пройдена!"

    def test_02_less_references_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_lit_ref" / "les_references.docx"
        checker = SWSectionLiteratureReferenceCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is False
        assert "содержит недостаточное количество ссылок" in result.result_str

    def test_03_chapter_and_subchapter(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_lit_ref" / "subchapter.docx"
        checker = SWSectionLiteratureReferenceCheck(report_path, "SW_ANALOGS_SECTIONS")
        result = checker.check()

        assert result.status is False
        assert "Каждый из подразделов" in result.result_str

    def test_04_search_references_format(self, checker):
        test_text = """
               В работе используются ссылки на источники [1] и [2].
               Также есть ссылки на диапазон [3-5].
               Встречается перечисление [6, 7, 8]."""
        references, ref_sequence = checker.search_references(test_text)
        expected_references = {1, 2, 3, 4, 5, 6, 7, 8}

        assert references == expected_references

