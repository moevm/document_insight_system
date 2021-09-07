from app.main.checks.base_check import BaseCheck, answer
from app.nlp.similarity_of_texts import check_similarity
from app.utils.parse_for_html import find_tasks_on_slides_feedback, tasks_conclusions_feedback
from app.utils.get_text_from_slides import get_text_from_slides

class FurtherDev(BaseCheck):
    def __init__(self, presentation, goals, conclusion):
        super().__init__(presentation)
        self.goals = goals
        self.conclusion = conclusion

    def check(self):
        goals = get_text_from_slides(self.presentation, self.goals)
        conclusions = get_text_from_slides(self.presentation, self.conclusion)
        if goals == "" or conclusions == "":
            return answer(False, None, 'Задач или заключения не существует')

        results = check_similarity(goals, conclusions)
        if results == -1:
            return answer(False, None, "Произошла ошибка!")
        else:
            return answer(results[1].get('found_dev'), results[1].get('dev_sentence'), results[1].get('dev_sentence'))
