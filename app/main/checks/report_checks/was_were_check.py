import re
from ..base_check import BaseReportCriterion, answer
from app.nlp.is_passive_was_were_sentence import is_passive_was_were_sentece

class ReportWasWereCheck(BaseReportCriterion):
    label = 'Проверка на пассивные конструкции, начинающиеся с Был/Была/Было/Были, которые можно убрать без потери смысла'
    description = ''
    id = 'report_was_were_check'

    def __init__(self, file_info):
        super().__init__(file_info)
    
    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, 'В отчёте недостаточно страниц. Нечего проверять.')
        detected = {}
        for page_index, page_text in self.file.pdf_file.get_text_on_page().items():
            sentences = re.split(r'(?<=[.!?…])\s+', page_text)
            for sentence_index, sentence in enumerate(sentences):
                if is_passive_was_were_sentece(sentence):
                    if page_index not in detected:
                        detected[page_index] = []
                    detected[page_index].append(f'{sentence_index+1}: {sentence}')
        if len(detected):
            result_str = 'Обнаружены конструкции (Был/Была/Было/Были), которые можно удалить без потери смысла:<br><br>'
            for page_index, messages in detected.items():
                result_str += f'Страница №{page_index+1}:<br>' + '<br>'.join(messages) + '<br><br>'
                print(f'Страница №{page_index+1}:<br>' + '<br>'.join(messages) + '<br><br>')
                print()
            result_score = 0
        else:
            result_str = 'Пройдена!'
            result_score = 1 
        return answer(result_score, result_str)