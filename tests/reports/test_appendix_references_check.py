from app.main.checks.report_checks.appendix_references import AppendixReferenceCheck
from tests.util.report_file_utils import create_report_file_info


class TestAppendixReferenceCheck:
    def _check(self, reports_fixture_dir, fixture):
        file_info = create_report_file_info(reports_fixture_dir / "appendix_references" / fixture)
        return AppendixReferenceCheck(file_info).check()

    def test_01_valid_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md")
        assert result["score"] == 1.0
        assert "Пройдена" in result["verdict"][0]

    def test_02_missing_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0] == "Не упомянуты в тексте следующие приложения: А"

    def test_03_no_appendices(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "no_appendices_valid.md")
        assert result["score"] == 1.0
        assert "Приложения не найдены" in result["verdict"][0]

    def test_04_reference_cases(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "cases_valid.md")
        assert result["score"] == 1.0

    def test_05_reference_in_subchapter(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "subchapter_valid.md")
        assert result["score"] == 1.0

    def test_06_multiple_missing_sorted(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "multiple_missing_invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": А, В")

    def test_07_reference_only_inside_appendix(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "appendix_only_reference_invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": Б")

    def test_08_reference_in_header_not_counted(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "header_reference_invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": А")

    def test_09_lowercase_letter_in_header(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "lowercase_header_valid.md")
        assert result["score"] == 1.0

    def test_10_chapter_about_application(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "app_chapter_valid.md")
        assert result["score"] == 1.0

    def test_11_enumeration_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "enumeration_valid.md")
        assert result["score"] == 1.0

    def test_12_plural_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "plural_reference_valid.md")
        assert result["score"] == 1.0

    def test_13_word_after_appendix_is_not_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "false_reference_invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": Д")

    def test_14_extra_spaces_in_header(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "double_space_invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": А")

    def test_15_appendix_mentioned_in_chapter_header(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "header_mention_valid.md")
        assert result["score"] == 1.0

    def test_16_preposition_is_not_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "preposition_invalid.md")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": В")

    def test_17_docx_valid_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.docx")
        assert result["score"] == 1.0
        assert "Пройдена" in result["verdict"][0]

    def test_18_docx_missing_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.docx")
        assert result["score"] == 0.0
        assert result["verdict"][0] == "Не упомянуты в тексте следующие приложения: А"

    def test_19_docx_application_genitive_is_not_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "app_modules_invalid.docx")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": А, Б, В")

    def test_20_docx_genitive_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "genitive_reference_valid.docx")
        assert result["score"] == 1.0

    def test_21_docx_lowercase_letter_is_not_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "lowercase_letter_invalid.docx")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": А")

    def test_22_docx_formatted_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "formatted_valid.docx")
        assert result["score"] == 1.0

    def test_23_docx_reference_in_table(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "table_valid.docx")
        assert result["score"] == 1.0

    def test_24_docx_reference_in_appendix_table_not_counted(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "table_in_appendix_invalid.docx")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": Б")

    def test_25_docx_table_before_chapters_not_counted(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "title_table_invalid.docx")
        assert result["score"] == 0.0
        assert result["verdict"][0].endswith(": А")

    def test_26_formatted_reference(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "formatted_valid.md")
        assert result["score"] == 1.0
