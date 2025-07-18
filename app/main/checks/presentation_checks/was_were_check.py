import re
from ..base_check import BasePresCriterion, answer
from app.nlp.is_passive_was_were_sentence import is_passive_was_were_sentece

class PresWasWereCheck(BasePresCriterion):
    label = 'Проверка на пассивные конструкции, начинающиеся с Был/Была/Было/Были, которые можно убрать без потери смысла'
    description = ''
    id = 'pres_was_were_check'

    def __init__(self, file_info):
        super().__init__(file_info)
    
    def check(self):
        detected = {}
        for slide_index, slide_text in enumerate(self.file.get_text_from_slides()):
            mock_slide_text = "Было проведено исследование. Было бы здорово. Как бы было здорово. Была проделана работа. Были сделаны шаги..." 
            sentences = re.split(r'(?<=[.!?…])\s+', mock_slide_text)
            for sentence_index, sentence in enumerate(sentences):
                if is_passive_was_were_sentece(sentence):
                    if slide_index not in detected:
                        detected[slide_index] = []
                    detected[slide_index].append(f'{sentence_index+1}: {sentence}')
        if len(detected):
            result_str = 'Обнаружены конструкции (Был/Была/Было/Были), которые можно удалить без потери смысла:<br><br>'
            for slide_index, messages in detected.items():
                result_str += f'Слайд №{slide_index+1}:<br>' + '<br>'.join(messages) + '<br><br>'
            result_score = 0
        else:
            result_str = 'Пройдена!'
            result_score = 1 
        return answer(result_score, result_str)