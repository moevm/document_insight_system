from ..base_check import BaseReportCriterion, answer
from ._content_similarity import content_and_intro, content_similarity, introduction_tasks


class CompareTasksAndContentCheck(BaseReportCriterion):
    label = 'Проверка соответствия задач и содержания'
    _description = 'Лексическое сходство задач и основного текста.'
    id = 'compare_tasks_and_content_check'

    def __init__(self, file_info, min_similarity=0.15, specific_min_similarity=0.05, min_tasks=3):
        super().__init__(file_info)
        self.min_similarity = min_similarity
        self.specific_min_similarity = specific_min_similarity
        self.min_tasks = min_tasks

    def check(self):
        intro, chapters = content_and_intro(self.file, self.file_type['report_type'])
        tasks = introduction_tasks(intro)
        if len(tasks) < self.min_tasks:
            return answer(False, f'Во введении найдено {len(tasks)} задач; требуется не менее {self.min_tasks}.')
        if not chapters:
            return answer(False, 'Не найден основной текст для сопоставления с задачами.')
        similarities = content_similarity(' '.join(tasks), chapters)
        average = sum(similarities.values()) / len(similarities) if similarities else 0
        errors = []
        if average < self.min_similarity:
            errors.append(f'Среднее сходство задач и разделов {average:.1%} ниже {self.min_similarity:.1%}.')
        for task in tasks:
            similarities = content_similarity(task, chapters)
            value = sum(similarities.values()) / len(similarities) if similarities else 0
            if value < self.specific_min_similarity:
                errors.append(f'Задача «{task}»: сходство {value:.1%} ниже {self.specific_min_similarity:.1%}.')
        return answer(not errors, '<br>'.join(errors) or f'Проверка пройдена. Среднее сходство: {average:.1%}.')
