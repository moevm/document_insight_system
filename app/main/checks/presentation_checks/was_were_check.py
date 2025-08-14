from ..base_check import BasePresCriterion, answer
from app.nlp.is_passive_was_were_sentence import CritreriaType, generate_output_text, get_was_were_sentences

class PresWasWereCheck(BasePresCriterion):
    label = 'Проверка на пассивные конструкции, начинающиеся с Был/Была/Было/Были, которые можно убрать без потери смысла'
    description = ''
    id = 'pres_was_were_check'

    def __init__(self, file_info, threshold=3):
        super().__init__(file_info)
        self.threshold = threshold
    
    def check(self):
        detected_sentences, total_sentences = get_was_were_sentences(self.file, CritreriaType.PRESENTATION)
        if total_sentences > self.threshold:
            result_str = generate_output_text(detected_sentences, CritreriaType.PRESENTATION)
            result_score = 0
        else:
            result_str = 'Пройдена!'
            result_score = 1 
        return answer(result_score, result_str)