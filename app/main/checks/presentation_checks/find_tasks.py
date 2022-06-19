from ..base_check import BaseCheck, answer
from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from app.utils.parse_for_html import find_tasks_on_slides_feedback
from app.utils.get_text_from_slides import get_text_from_slides

class FindTasks(BaseCheck):
    def __init__(self, file, keyword, intersection_number):
        super().__init__(file)
        self.keyword = keyword
        self.intersection_number = intersection_number

    def check(self):
        get_goals = get_text_from_slides(self.file, self.keyword)
        if get_goals == "":
            return answer(False, 'Слайд "Задачи" не найден')

        titles = self.file.get_titles()
        slides_with_tasks = find_tasks_on_slides(get_goals, titles, self.intersection_number)

        if slides_with_tasks == 0:
            return answer(True, "Все задачи найдены на слайдах")
        elif len(slides_with_tasks) == 3 :
            return answer(False, *find_tasks_on_slides_feedback(slides_with_tasks))
        else:
            return answer(False, slides_with_tasks)
