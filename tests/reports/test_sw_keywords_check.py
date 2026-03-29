from app.main.checks.report_checks.sw_keywords_check import SWKeywordsCheck

class TestSWKeywordsCheck:

    def test_01_valid_keywords(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "valid.docx"
        checker = SWKeywordsCheck(report_path)
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_02_missing_keywords_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "missing_chapter.docx"
        checker = SWKeywordsCheck(report_path)
        result = checker.check()
        assert result.status is False
        assert result.result_str == 'Раздел "Ключевые слова" не найден'

    def test_03_less_keywords(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "less_keywords.docx"
        checker = SWKeywordsCheck(report_path)
        result = checker.check()

        assert result.status is False
        assert "Не пройдена!" in result.result_str

    def test_04_missing_word_in_text(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "keywords" / "missing_word.docx"
        checker = SWKeywordsCheck(report_path)
        result = checker.check()

        assert result.status is False
        assert "Не пройдена!" in result.result_str