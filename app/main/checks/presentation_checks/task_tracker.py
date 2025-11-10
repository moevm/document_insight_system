from app.utils.get_text_from_slides import get_text_from_slides
from app.nlp.stemming import Stemming
from ..base_check import BasePresCriterion, answer, morph

class TaskTracker(BasePresCriterion):
    label = "Поиск недопустимых задач"
    description = 'Не пропускать задачи из серии "доделать, решить, описать"'
    id = 'task_tracker'

    def __init__(self, file_info, goal_and_tasks='Цель и задачи', deny_list=['доделать', 'решить', 'описать']):
        super().__init__(file_info)
        self.goal_and_tasks = goal_and_tasks
        self.deny_list = [morph.parse(word)[0].normal_form for word in deny_list]

    def check(self):
        goal_and_tasks = get_text_from_slides(self.file, self.goal_and_tasks)
        if goal_and_tasks == "":
            return answer(False, 'Слайда "Цель и задачи" не существует')
        stemming = Stemming()
        stemming.parse_text(goal_and_tasks, True)
        word_in_docs = []
        for filtered_doc in stemming.filtered_docs:
            for word in filtered_doc:
                if word in self.deny_list:
                    word_in_docs.append(word)
        if word_in_docs:
            return answer(False, f'Задачи не должны содержать слова: {self.deny_list}! Обнаруженные слова: {word_in_docs}.')
        else:
            return answer(True, 'Задачи сформулированы корректно!')