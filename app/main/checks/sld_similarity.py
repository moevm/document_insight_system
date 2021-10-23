from app.main.checks.base_check import BaseCheck, answer
from app.nlp.similarity_of_texts import check_similarity
from app.utils.parse_for_html import find_tasks_on_slides_feedback, tasks_conclusions_feedback
from app.utils.get_text_from_slides import get_text_from_slides

class SldSimilarity(BaseCheck):
    def __init__(self, presentation, goals, conclusion, actual_number):
        super().__init__(presentation)
        self.goals = goals
        self.conclusion = conclusion
        self.actual_number = actual_number

    def check(self):
        goals = get_text_from_slides(self.presentation, self.goals)
        conclusions = get_text_from_slides(self.presentation, self.conclusion)
        if goals == "" or conclusions == "":
            return answer(False, 'Задач или заключения не существует')

        results = check_similarity(goals, conclusions)

        return answer(results[0] >= self.actual_number, *tasks_conclusions_feedback(results))
