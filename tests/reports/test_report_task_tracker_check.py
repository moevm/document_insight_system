from app.main.checks.report_checks.task_tracker import ReportTaskTracker
from tests.util import create_report_file_info

class TestReportTaskTrackerCheck:

    def test_01_valid_report(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "task_tracker" / "valid.docx"
        checker = ReportTaskTracker(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 1.0
        assert result["verdict"][0] == "Задачи сформулированы корректно!"

    def test_02_forbidden_words(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "task_tracker" / "forbidden_task.docx"
        checker = ReportTaskTracker(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Задачи не должны содержать слова" in result["verdict"][0]
        assert "Обнаруженные слова" in result["verdict"][0]

    def test_03_missing_chapter(self, reports_fixture_dir):
        report_path = reports_fixture_dir / "task_tracker" / "missing_chapter.docx"
        checker = ReportTaskTracker(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Раздел Введение не обнаружен!"
