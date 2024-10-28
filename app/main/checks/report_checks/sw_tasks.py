from ..base_check import BaseReportCriterion, answer
from logging import getLogger


logger = getLogger('root')


class SWTasksCheck(BaseReportCriterion):
    label = "Проверка количества задач исследования"
    description = "Проверка количества задач исследования"
    id = "sw_tasks_check"
    priority = True

    def __init__(self, file_info, min_tasks=3, max_tasks=5):
        super().__init__(file_info)
        
        self.min_tasks = min_tasks
        self.max_tasks = max_tasks
    
    def check(self):
        self.file.make_chapters('VKR')
        for chapter in self.file.chapters:
            if "Задачи" in chapter['text']:
                if self.min_tasks <= len(chapter['child']) <= self.max_tasks:
                    return answer(1, "Проверка пройдена!")
                feedback = f"Количество задач исследования должно быть в диапазоне [{self.min_tasks};{self.max_tasks}], сейчас их {len(chapter['child'])}"
                return answer(0, feedback)
        return answer(1, "Проверка пройдена!")
