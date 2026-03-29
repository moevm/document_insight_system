from app.main.checks.report_checks.sw_section_size import SWSectionSizeCheck

class TestSWSectionSizeCheck:

    def test_01_valid_section_size(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_size" / "valid.docx"
        checker = SWSectionSizeCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Проверка пройдена!"

    def test_02_extra_words_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_size" / "extra_words.docx"
        checker = SWSectionSizeCheck(report_path,"SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is False
        assert "по количеству слов" in result.result_str

    def test_03_extra_sentences_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_size" / "extra_sentences.docx"
        checker = SWSectionSizeCheck(report_path, "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result.status is False
        assert "по количеству предложений" in result.result_str

