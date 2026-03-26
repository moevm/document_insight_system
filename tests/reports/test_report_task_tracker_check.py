from app.main.checks.report_checks.task_tracker import ReportTaskTracker

class TestReportTaskTrackerCheck:

    def test_01_valid_report(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "task_tracker" / "valid.docx"
        checker = ReportTaskTracker(report_path)
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Задачи сформулированы корректно!"

    def test_02_forbidden_words(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "task_tracker" / "forbidden_task.docx"
        checker = ReportTaskTracker(report_path)
        result = checker.check()

        assert result.status is False
        assert "Задачи не должны содержать слова" in result.result_str
        assert "Обнаруженные слова" in result.result_str

    def test_03_missing_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "task_tracker" / "missing_chapter.docx"
        checker = ReportTaskTracker(report_path)
        result = checker.check()

        assert result.status is False
