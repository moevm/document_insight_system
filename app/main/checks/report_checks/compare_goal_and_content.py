from ..base_check import BaseReportCriterion, answer

class CompareGoalAndContentCheck(BaseReportCriterion):
    description = "Проверка соответствия цели, задач и содержания"
    id = 'compare_goal_and_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        return answer(True, "Проверка")