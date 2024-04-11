from ..base_check import BaseReportCriterion, answer


class CompareGoalAndContentCheck(BaseReportCriterion):
    description = "Проверка соответствия цели, задач и содержания"
    id = 'compare_goal_and_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.goal = ""
        self.tasks = []
        self.main_text = []

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        self.late_init()
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = ""
        for text_on_page in self.file.pdf_file.get_text_on_page().values():
            if text_on_page.split()[0].lower() != "введение":
                continue
            goal_index = text_on_page.find("Цель")
            tasks_index = text_on_page.find("Задачи")
            if goal_index != -1 and tasks_index != -1:
                goal_start = goal_index + len("Цель") + 1
                goal_end = tasks_index
                self.goal = text_on_page[goal_start:goal_end].strip()
                tasks_start = tasks_index + len("Задачи") + 1
                tasks_end = text_on_page.find(".", tasks_start)
                self.tasks = text_on_page[tasks_start:tasks_end].split('\n')
                result = f"tasks equal {text_on_page[tasks_start:tasks_end]} {tasks_start} {tasks_end}"
            elif goal_index == -1:
                return answer(False, "В введении не написана цель работы")
            elif tasks_index == -1:
                return answer(False, "В введении не написаны задачи")
        result = f"Цель: {self.goal}, задачи: {self.tasks}"
        return answer(True, result)