from app.main.checks.base_check import BaseCheck, answer
from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from app.utils.parse_for_html import find_tasks_on_slides_feedback

class FindTasks(BaseCheck):
    def __init__(self, presentation, goals, intersection_number):
        super().__init__(presentation)
        self.goals = goals
        self.intersection_number = intersection_number

    def check(self):
        if self.goals == "":
            return answer(False, None, 'Слайд "Задачи" не найден')

        titles = self.presentation.get_titles()
        slides_with_tasks = find_tasks_on_slides(self.goals, titles, self.intersection_number)

        if slides_with_tasks == 0:
            return answer(True, "Все задачи найдены на слайдах", "Все задачи найдены на слайдах")
        elif len(slides_with_tasks) == 3 :
            return answer(False, slides_with_tasks, *find_tasks_on_slides_feedback(slides_with_tasks))
        elif len(slides_with_tasks) == 1:
            return answer(False, slides_with_tasks, slides_with_tasks)
