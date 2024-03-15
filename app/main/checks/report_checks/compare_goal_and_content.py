import re

from ..base_check import BaseReportCriterion, answer, morph


class CompareGoalAndContentCheck(BaseReportCriterion):
    description = "Проверка соответствия цели, задач и содержания"
    id = 'compare_goal_and_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.goal = ""
        self.problems = []
        self.main_text = []

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        self.late_init()
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = []
        for header in self.headers:
            result.append(header["text"][0:10])

        return answer(True, " ".join(result))