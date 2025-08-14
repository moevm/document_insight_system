from ..base_check import BaseReportCriterion, answer
from app.nlp.is_passive_was_were_sentence import CritreriaType, generate_output_text, get_was_were_sentences

class ReportWasWereCheck(BaseReportCriterion):
    label = 'Проверка на пассивные конструкции, начинающиеся с Был/Была/Было/Были, которые можно убрать без потери смысла'
    description = ''
    id = 'report_was_were_check'

    def __init__(self, file_info, threshold=3):
        super().__init__(file_info)
        self.threshold = threshold
    
    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, 'В отчёте недостаточно страниц. Нечего проверять.')
        detected, total_sentences = get_was_were_sentences(self.file, CritreriaType.REPORT)
        if total_sentences > self.threshold:
            result_str = generate_output_text(detected, CritreriaType.REPORT)
            result_score = 0
        else:
            result_str = 'Пройдена!'
            result_score = 1 
        return answer(result_score, result_str)