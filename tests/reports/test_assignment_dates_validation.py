import pytest

from app.main.checks.report_checks.assignment_dates_validation import ReportAssignmentDatesValidationCheck
from tests.util.report_file_utils import create_report_file_info


class TestAssignmentDatesValidation:
    @pytest.mark.parametrize(
        "required_days, excepted_score",
        [
            (7, 1.0),
            (6, 1.0),
            (3, 0.0),
        ],
    )
    def test_01_dates_exists(self, reports_fixture_dir, required_days, excepted_score):
        file_info = create_report_file_info(reports_fixture_dir / "assignment_dates_validation" / "correct_dates.docx")
        checker = ReportAssignmentDatesValidationCheck(
            file_info, date_of_issue="2026-11-24", required_days=required_days
        )
        result = checker.check()

        assert result["score"] == excepted_score

    def test_02_empty_dates(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / "assignment_dates_validation" / "empty_dates.docx")
        checker = ReportAssignmentDatesValidationCheck(file_info, date_of_issue="2026-11-24", required_days=7)
        result = checker.check()

        assert result["score"] == 0.0

    @pytest.mark.parametrize("file", ["incorrect_dates1.docx", "incorrect_dates2.docx"])
    def test_03_incorrect_dates(self, reports_fixture_dir, file):
        file_info = create_report_file_info(reports_fixture_dir / "assignment_dates_validation" / file)
        checker = ReportAssignmentDatesValidationCheck(file_info, date_of_issue="2026-11-24", required_days=7)
        result = checker.check()

        assert result["score"] == 0.0

    def test_04_start_date_after_end_date(self, reports_fixture_dir):
        file_info = create_report_file_info(
            reports_fixture_dir / "assignment_dates_validation" / "start_date_after_end_date.docx"
        )
        checker = ReportAssignmentDatesValidationCheck(file_info, date_of_issue="2026-11-24", required_days=7)
        result = checker.check()

        assert result["score"] == 0.0
