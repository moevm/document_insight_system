import re
from ..base_check import BaseReportCriterion, answer


class KeyWordsReportCheck(BaseReportCriterion):
    label = 'Проверка наличия раздела "Ключевые слова"'
    description = 'Раздел идет сразу после названия работы и содержит не менее трех ключевых слов'
    id = 'Key_words_report_check'

    def __init__(self, file_info, min_key_words = 3):
        super().__init__(file_info)
        self.min_key_words = min_key_words

    def check(self):
        key_words_chapter = self.file.paragraphs[1].lower()
        if 'ключевые слова' not in key_words_chapter:
            return answer(False, 'Раздел "Ключевые слова" не найден')
        cleaned_str = re.sub(r'<[^>]*>', '', key_words_chapter)
        final_str = cleaned_str.replace('ключевые слова', '').replace(':','').replace(' ', '')
        key_words = final_str.split(',')
        if len(key_words) >= self.min_key_words:
            return answer(True, 'Пройдена!')
        else:
            return answer(False, f'Не пройдена! Количество ключевых слов должно быть не менее {self.min_key_words}')
