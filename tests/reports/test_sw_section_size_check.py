from app.main.checks.report_checks.sw_section_size import SWSectionSizeCheck
from tests.util import create_report_file_info

class TestSWSectionSizeCheck:

    def test_01_valid_section_size(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_size" / "valid.md"
        checker = SWSectionSizeCheck(create_report_file_info(report_path), "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result["score"] == 1.0
        assert result["verdict"][0] == "Проверка пройдена!"

    def test_02_extra_words_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_size" / "extra_words.md"
        checker = SWSectionSizeCheck(create_report_file_info(report_path),"SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result["score"] == 0.0
        assert "по количеству слов" in result["verdict"][0]

    def test_03_extra_sentences_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_section_size" / "extra_sentences.md"
        checker = SWSectionSizeCheck(create_report_file_info(report_path), "SW_KEY_QUESTIONS_SECTIONS")
        result = checker.check()

        assert result["score"] == 0.0
        assert "по количеству предложений" in result["verdict"][0]

