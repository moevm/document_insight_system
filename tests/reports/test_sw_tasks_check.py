import pytest

from app.main.checks.report_checks.sw_tasks import SWTasksCheck
from tests.util import create_report_file_info


class TestSWTasksCheck:
    def test_01_valid_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "valid.md"
        checker = SWTasksCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 1.0
        assert result["verdict"][0] == "Проверка пройдена!"

    def test_02_less_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "less_task.md"
        checker = SWTasksCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Количество задач исследования должно быть в рамках" in result["verdict"][0]

    def test_03_extra_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "extra_task.md"
        checker = SWTasksCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert "Количество задач исследования должно быть в рамках" in result["verdict"][0]

    @pytest.mark.parametrize(
        "docx_file_name, is_corect, count_task",
        [
            ("invalid_less_tasks.docx", False, 1),
            ("invalid_more_tasks.docx", False, 8),
            ("invalid_tasks_not_found.docx", False, 0),
            ("invalid_tasks_is_empty.docx", False, 0),
            ("valid.docx", True, None),
            ("valid_missing_stop_marker.docx", True, None),
            ("valid_start_marker_is_last.docx", True, None),
            ("valid_stop_marker_before_start_marker.docx", True, None),
            ("valid_task_without_marks.docx", True, None),
        ],
    )
    def test_04_correct_find_tasks(self, reports_fixture_dir, docx_file_name, is_corect, count_task):
        report_path = reports_fixture_dir / "sw_tasks" / docx_file_name
        checker = SWTasksCheck(create_report_file_info(report_path))
        result = checker.check()

        if not is_corect:
            verdict = result.get("verdict")[0]
            real_find_count_task = int(list(filter(lambda x: x.isdigit(), verdict))[-1])

            assert count_task == real_find_count_task
        else:
            assert result.get("score") == 1.0
