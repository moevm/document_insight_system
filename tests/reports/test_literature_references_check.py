from app.main.checks.report_checks.literature_references import ReferencesToLiteratureCheck
from tests.util.report_file_utils import create_report_file_info

class TestReferencesToLiteratureCheck:

    def test_01_valid_references(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "literature_references" / "valid.md")
        checker = ReferencesToLiteratureCheck(file_info)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_unused_sources(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "literature_references" / "invalid.md")
        checker = ReferencesToLiteratureCheck(file_info)
        result = checker.check()
        assert result["score"] < 1.0
