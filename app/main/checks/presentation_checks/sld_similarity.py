from nlp.similarity_of_texts import check_similarity
from utils import get_text_from_slides, tasks_conclusions_feedback

from ..base_check import BasePresCriterion, answer


class SldSimilarity(BasePresCriterion):
    description = "Соответствие заключения задачам"
    id = 'conclusion_actual'

    def __init__(self, file_info, goals='Цель и задачи', conclusion='Заключение', min_percent=50):
        super().__init__(file_info)
        self.goals = goals
        self.conclusion = conclusion
        self.actual_number = min_percent

    def check(self):
        goals = get_text_from_slides(self.file, self.goals)
        conclusions = get_text_from_slides(self.file, self.conclusion)
        if goals == "" or conclusions == "":
            return answer(False, 'Задач или заключения не существует')

        results = check_similarity(goals, conclusions)

        return answer(results[0] >= self.actual_number, *tasks_conclusions_feedback(results))
