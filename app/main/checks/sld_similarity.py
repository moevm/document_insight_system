from app.main.checks.base_check import BaseCheck, answer
from app.nlp.similarity_of_texts import check_similarity
from app.utils.parse_for_html import find_tasks_on_slides_feedback, tasks_conclusions_feedback

class SldSimilarity(BaseCheck):
    def __init__(self, presentation, goals, conclusions, actual_number):
        super().__init__(presentation)
        self.goals = goals
        self.conclusions = conclusions
        self.actual_number = actual_number

    def check(self):
        if self.goals == "" or self.conclusions == "":
            return answer(False, None, 'Задач или заключения не существует'), answer(False, None, 'Задач или заключения не существует')

        results = check_similarity(self.goals, self.conclusions)
        if results == -1:
            return answer(False, None, "Произошла ошибка!"), answer(False, None, "Произошла ошибка!")
        else:
            return (answer(results[0] >= self.actual_number, results[0], *tasks_conclusions_feedback(results)),
                    answer(results[1].get('found_dev'), results[1].get('dev_sentence'), results[1].get('dev_sentence')))
