import re
from datetime import date, timedelta

from app.main.checks.base_check import BaseReportCriterion, answer

EXAMPLE_DATE_OF_ISSUE = "2026-11-24"
EXAMPLE_REQUIRED_DAYS = 7
PATTERN = r'[«"]\s*(\d{1,2})\s*[»"]\s+(\S+)\s+(\d{2,4})\s*г\.?'

MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def parse_dates(text):
    matches = re.findall(PATTERN, text)

    if not matches:
        raise ValueError("Не найдена дата")

    return [[int(year), MONTHS.get(month.lower(), month), int(day)] for day, month, year in matches]


class ReportAssignmentDatesValidationCheck(BaseReportCriterion):
    label = "Проверка валидность назначенных дат"
    _description = "Проверяет корректность даты назначения и сдачи работы"
    id = "assignment_dates_validation"
    priority = True

    def __init__(self, file_info, date_of_issue=EXAMPLE_DATE_OF_ISSUE, required_days=EXAMPLE_REQUIRED_DAYS):
        super().__init__(file_info)
        self.date_of_issue = date.fromisoformat(date_of_issue)
        self.required_days = required_days

    def check(self):
        headers = self.file.make_headers("VKR")
        task_header = next(header for header in headers if header.get("key", None) == "задание")
        task_number_page = task_header.get("page", None)
        page_text = self.file.pdf_file.get_text_on_page(task_number_page, task_number_page).get(task_number_page, '')

        try:
            start, end = parse_dates(page_text)
            start, end = date(*start), date(*end)
        except ValueError:
            return answer(
                False,
                f"Неверно указана дата выдачи задания и/или дата представления к защите на {task_number_page} стр.",
            )

        if start > end:
            return answer(False, "Дата сдачи не может быть раньше даты выдачи задания.")

        if start != self.date_of_issue or end > self.date_of_issue + timedelta(days=self.required_days):
            return answer(
                False,
                f"Неверно указана дата выдачи задания и/или дата представления к защите на {task_number_page} стр.",
            )
        return answer(True, "Проверка пройдена!")
