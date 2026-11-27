import pytest

from app.main.checks.report_checks.task_tracker import ReportTaskTracker
from tests.util.report_file_utils import create_report_file_info


class TestReportTaskTracker:
    @pytest.mark.parametrize(
        "file, min_tasks, max_tasks, excepted_score",
        [
            ("valid.docx", 1, 6, 1.0),
            ("valid.docx", 1, 5, 1.0),
            ("valid.docx", 5, 10, 1.0),
            ("valid.docx", 5, 5, 1.0),
            ("valid.docx", 1, 3, 0.0),
            ("valid.docx", 6, 10, 0.0),
            ("valid.docx", 6, 6, 0.0),
        ],
    )  # valid.docx has 5 tasks
    def test_01_correct_answer_by_number_of_tasks(
        self, reports_fixture_dir, file, min_tasks, max_tasks, excepted_score
    ):
        file_info = create_report_file_info(reports_fixture_dir / "task_tracker" / file)
        checker = ReportTaskTracker(
            file_info=file_info, deny_list=(), min_count_tasks=min_tasks, max_count_tasks=max_tasks
        )
        result = checker.check()

        assert result["score"] == excepted_score

    @pytest.mark.parametrize(
        "min_tasks, max_tasks, excepted_score",
        [
            (1, 3, 0.0),
            (0, 3, 1.0),
        ],
    )
    def test_02_without_tasks(self, reports_fixture_dir, min_tasks, max_tasks, excepted_score):
        file_info = create_report_file_info(reports_fixture_dir / "task_tracker" / "without_tasks.docx")
        checker = ReportTaskTracker(
            file_info=file_info, deny_list=(), min_count_tasks=min_tasks, max_count_tasks=max_tasks
        )
        result = checker.check()

        assert result["score"] == excepted_score

    def test_03_forbidden_tasks(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "task_tracker" / "forbidden_task.docx")
        checker = ReportTaskTracker(file_info=file_info, min_count_tasks=1, max_count_tasks=1000)
        result = checker.check()

        assert result["score"] == 0.0

    def test_04_valid_not_found_deny_tasks(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "task_tracker" / "valid.docx")
        checker = ReportTaskTracker(file_info=file_info, min_count_tasks=1, max_count_tasks=1000)
        result = checker.check()

        assert result["score"] == 1.0

    def test_05_missing_chapter(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "task_tracker" / "missing_chapter.docx")
        checker = ReportTaskTracker(file_info=file_info, min_count_tasks=1, max_count_tasks=1000)
        result = checker.check()

        assert result["score"] == 0.0
