from app.main.checks.report_checks.sw_tasks import SWTasksCheck

class TestSWTasksCheck:

    def test_01_valid_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "valid.docx"
        checker = SWTasksCheck(report_path)
        result = checker.check()

        assert result.status is True
        assert result.result_str == "Проверка пройдена!"

    def test_02_less_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "less_task.docx"
        checker = SWTasksCheck(report_path)
        result = checker.check()

        assert result.status is False
        assert   "Количество задач исследования должно быть в диапазоне" in result.result_str

    def test_03_extra_task_count(selfs, reports_fixture_dir):
        report_path = reports_fixture_dir / "sw_tasks" / "extra_task.docx"
        checker = SWTasksCheck(report_path)
        result = checker.check()

        assert result.status is False
        assert  "Количество задач исследования должно быть в диапазоне" in result.result_str