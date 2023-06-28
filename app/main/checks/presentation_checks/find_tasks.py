from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from app.utils.get_text_from_slides import get_text_from_slides
from app.utils.parse_for_html import find_tasks_on_slides_feedback
from ..base_check import BasePresCriterion, answer


class FindTasks(BasePresCriterion):
    description = "Наличие слайдов, посвященных задачам"
    id = 'slide_every_task'

    def __init__(self, file_info, min_percent=50, keyword='Цель и задачи'):
        super().__init__(file_info)
        self.keyword = keyword
        self.intersection_number = min_percent

    def check(self):
        get_goals = get_text_from_slides(self.file, self.keyword)
        if get_goals == "":
            return answer(False, 'Слайд "Задачи" не найден')

        titles = self.file.get_titles()
        slides_with_tasks = find_tasks_on_slides(get_goals, titles, self.intersection_number)

        if isinstance(slides_with_tasks, dict):
            if slides_with_tasks['not_found'] and self.intersection_number > slides_with_tasks['found_ratio'] * 100:
                return answer(slides_with_tasks['found_ratio'], *find_tasks_on_slides_feedback(slides_with_tasks))
            else:
                return answer(1, "Все задачи найдены на слайдах")
        else:
            return answer(False, slides_with_tasks)
