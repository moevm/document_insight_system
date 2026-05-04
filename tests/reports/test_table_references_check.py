from app.main.checks.report_checks.table_references import TableReferences
from tests.util import create_report_file_info

class TestTableReferences:

    def test_01_valid_references(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "table_references" / "valid.docx"
        checker = TableReferences(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 1.0
        assert result["verdict"][0] == "Пройдена!"

    def test_02_missing_references(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "table_references" / "missing_references.docx"
        checker = TableReferences(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Упомянуты не все таблицы" in result["verdict"][0]

    def test_03_extra_references(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "table_references" / "extra_references.docx"
        checker = TableReferences(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Упомянуты несуществующие таблицы" in result["verdict"][0]