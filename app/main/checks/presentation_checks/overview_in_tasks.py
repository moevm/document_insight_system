from app.utils.get_text_from_slides import get_text_from_slides
from app.nlp.stemming import Stemming
from ..base_check import BasePresCriterion, answer, morph

class OverviewInTasks(BasePresCriterion):
    label = "Проверка наличия обзора в числе задач"
    description = 'В числе задач должен присутсвовать обзор/анализ предметной области'
    id = 'overview_in_tasks'

    def __init__(self, file_info, goal_and_tasks='Цель и задачи', keywords=['обзор', 'анализ']):
        super().__init__(file_info)
        self.goal_and_tasks = goal_and_tasks
        self.keywords = [morph.parse(word)[0].normal_form for word in keywords]

    def check(self):
        goal_and_tasks = get_text_from_slides(self.file, self.goal_and_tasks)
        if goal_and_tasks == "":
            return answer(False, 'Слайда "Цель и задачи" не существует')
        stemming = Stemming()
        stemming.parse_text(goal_and_tasks, True)
        for filtered_doc in stemming.filtered_docs:
            for word in filtered_doc:
                if word in self.keywords:
                    return answer(True, 'Пройдена!')
        return answer(False, 'В списке задач требуется наличие обзора!')
