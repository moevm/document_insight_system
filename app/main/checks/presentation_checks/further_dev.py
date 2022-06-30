from app.nlp.similarity_of_texts import check_similarity
from app.utils.get_text_from_slides import get_text_from_slides
from app.utils.parse_for_html import format_header
from .find_def_sld import FindDefSld
from ..base_check import BasePresCriterion, answer


class FurtherDev(BasePresCriterion):
    description = "Наличие направлений дальнейшего развития"
    id = 'future_dev'

    def __init__(self, file_info, goals='Цель и задачи', conclusion='Заключение'):
        super().__init__(file_info)
        self.goals = goals
        self.conclusion = conclusion

    def check(self):
        concl_sld = FindDefSld({'file': self.file, 'filename': self.filename, 'pdf_id': self.pdf_id},
                               self.conclusion).check()
        goals = get_text_from_slides(self.file, self.goals)
        conclusions = get_text_from_slides(self.file, self.conclusion)
        if goals == "" or conclusions == "":
            return answer(False, 'Задач или заключения не существует')

        results = check_similarity(goals, conclusions)

        return answer(results[1].get('found_dev'),
                      format_header(results[1].get('dev_sentence')), *concl_sld['verdict'])
