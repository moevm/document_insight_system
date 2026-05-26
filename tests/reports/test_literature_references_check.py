from unittest.mock import MagicMock
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
        assert "Упомянуты не все источники" in result["verdict"][0]

    def test_03_range_references(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "literature_references" / "valid.md")
        file_info['file'].paragraphs = ["Text with range [1-3].", "Another part [4,5]."]
        file_info['file'].find_literature_vkr = MagicMock(return_value={"number": 2, "child": [{"text": "Source 1"}, {"text": "Source 2"}, {"text": "Source 3"}, {"text": "Source 4"}, {"text": "Source 5"}]})
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReferencesToLiteratureCheck(file_info)
        result = checker.check()
        assert result["score"] == 1.0

    def test_04_mixed_references(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "literature_references" / "valid.md")
        file_info['file'].paragraphs = ["Mixed refs [1,2,4-5].", "Missing three."]
        file_info['file'].find_literature_vkr = MagicMock(return_value={"number": 2, "child": [{"text": "S1"}, {"text": "S2"}, {"text": "S3"}, {"text": "S4"}, {"text": "S5"}]})
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReferencesToLiteratureCheck(file_info)
        result = checker.check()
        assert result["score"] < 1.0
        assert "3" in result["verdict"][0]

    def test_05_empty_literature(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "literature_references" / "invalid.md")
        file_info['file'].find_literature_vkr = MagicMock(return_value={"number": 2, "child": []})
        file_info['file_type']['report_type'] = 'VKR'
        checker = ReferencesToLiteratureCheck(file_info)
        result = checker.check()
        assert result["score"] == 0.0
        assert "не найдено ни одного источника" in result["verdict"][0]
