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
        assert   "Количество задач исследования должно быть в диапазоне" in result["verdict"][0]

    def test_03_extra_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "extra_task.md"
        checker = SWTasksCheck(create_report_file_info(report_path))
        result = checker.check()

        assert result["score"] == 0.0
        assert  "Количество задач исследования должно быть в диапазоне" in result["verdict"][0]