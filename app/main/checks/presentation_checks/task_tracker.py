from app.utils.get_text_from_slides import get_text_from_slides
from app.nlp.stemming import Stemming
from ..base_check import BasePresCriterion, answer, morph

class TaskTracker(BasePresCriterion):
    label = "Поиск недопустимых задач"
    description = 'Не пропускать задачи из серии "доделать, решить, описать"'
    id = 'task_tracker'

    def __init__(self, file_info, goal_and_tasks='Цель и задачи'):
        super().__init__(file_info)
        self.goal_and_tasks = goal_and_tasks

    def check(self):
        goal_and_tasks = get_text_from_slides(self.file, self.goal_and_tasks)
        if goal_and_tasks == "":
            return answer(False, 'Слайда "Цель и задачи" не существует')
        stemming = Stemming()
        stemming.parse_text(goal_and_tasks, True)
        verbs_in_docs = []
        for filtered_doc in stemming.filtered_docs:
            word = filtered_doc[0]
            if 'INFN' in morph.parse(word)[0].tag:
                verbs_in_docs.append(word)
        if verbs_in_docs:
            return answer(False, f'Задачи не должны начинаться с глаголов! Обнаруженные глаголы: {verbs_in_docs}.')
        else:
            return answer(True, 'Задачи сформулированы корректно!')
        