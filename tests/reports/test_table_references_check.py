from app.main.checks.report_checks.table_references import TableReferences

class TestTableReferences:

    def test_01_valid_references(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "table_references" / "valid.docx"
        checker = TableReferences(report_path)
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Пройдена!"

    def test_02_missing_references(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "table_references" / "missing_references.docx"
        checker = TableReferences(report_path)
        result = checker.check()

        assert result.status is False
        assert result.result_str == "Упомянуты не все таблицы"

    def test_03_extra_references(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "table_references" / "extra_references.docx"
        checker = TableReferences(report_path)
        result = checker.check()

        assert result.status is False
        assert result.result_str == "Упомянуты несуществующие таблицы"