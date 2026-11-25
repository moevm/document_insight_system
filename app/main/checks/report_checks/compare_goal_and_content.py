import re

from ..base_check import BaseReportCriterion, answer
from ._content_similarity import content_and_intro, content_similarity


class CompareGoalAndContentCheck(BaseReportCriterion):
    label = 'Проверка соответствия цели и содержания'
    _description = 'Лексическое сходство цели и основного текста.'
    id = 'compare_goal_and_content_check'

    def __init__(self, file_info, min_similarity=0.1):
        super().__init__(file_info)
        self.min_similarity = min_similarity

    def check(self):
        intro, chapters = content_and_intro(self.file, self.file_type['report_type'])
        intro_text = '\n'.join(child['text'] for child in intro['child']) if intro else ''
        match = re.search(
            r'\bцель(?:ю)?(?:\s+(?:данной\s+)?работы)?\s*(?:является|[:—-])?\s*([^\n.!?]+)', intro_text, re.I
        )
        if not match:
            return answer(False, 'Во введении не найдена цель работы.')
        if not chapters:
            return answer(False, 'Не найден основной текст для сопоставления с целью.')
        similarities = content_similarity(match.group(1), chapters)
        average = sum(similarities.values()) / len(similarities) if similarities else 0
        return answer(
            average >= self.min_similarity,
            f'Среднее лексическое сходство цели и разделов: {average:.1%}; требуется {self.min_similarity:.1%}.',
        )
