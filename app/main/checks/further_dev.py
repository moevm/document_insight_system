from app.main.checks.base_check import BaseCheck, answer
from app.nlp.similarity_of_texts import check_similarity
from app.utils.parse_for_html import find_tasks_on_slides_feedback, tasks_conclusions_feedback
from app.utils.get_text_from_slides import get_text_from_slides
from app.utils.parse_for_html import format_header
from .find_def_sld import FindDefSld

class FurtherDev(BaseCheck):
    def __init__(self, presentation, goals, conclusion, pdf_id):
        super().__init__(presentation)
        self.goals = goals
        self.conclusion = conclusion
        self.pdf_id = pdf_id

    def check(self):
        concl_sld = FindDefSld(self.presentation, 'Заключение', self.pdf_id).check()
        goals = get_text_from_slides(self.presentation, self.goals)
        conclusions = get_text_from_slides(self.presentation, self.conclusion)
        if goals == "" or conclusions == "":
            return answer(False, 'Задач или заключения не существует')

        results = check_similarity(goals, conclusions)

        return answer(results[1].get('found_dev'),
                      format_header(results[1].get('dev_sentence')), *concl_sld['verdict'])
