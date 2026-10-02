from app.main.checks.report_checks.sw_keywords_check import SWKeywordsCheck
from tests.util import create_report_file_info


class TestSWKeywordsCheck:

    def test_01_valid_keywords(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "valid.md"
        checker = SWKeywordsCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 1.0
        assert result["verdict"][0] == "Пройдена!"

    def test_02_missing_keywords_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "missing_chapter.md"
        checker = SWKeywordsCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert result["verdict"][0] == 'Раздел "Ключевые слова" не найден'

    def test_03_less_keywords(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "less_keywords.md"
        checker = SWKeywordsCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Не пройдена! Количество ключевых слов должно быть не менее 3" in result["verdict"][0]

    def test_04_missing_word_in_text(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "missing_word.md"
        checker = SWKeywordsCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Не пройдена!" in result["verdict"][0]