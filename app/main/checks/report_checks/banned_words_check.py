import re
import pymorphy2
from ..base_check import BaseCheck, answer


class ReportBannedWordsCheck(BaseCheck):
    def __init__(self, file, words, min_count, max_count):
        super().__init__(file)
        self.words = words
        self.min_count = min_count
        self.max_count = max_count

    def check(self):
        parsed_pdf = self.file.get_parsed_pdf()
        text = parsed_pdf.get_text_on_page().items()
        result_str = ''
        count = 0
        morph = pymorphy2.MorphAnalyzer()
        for k, v in text:
            lines_on_page = re.split(r'\n', v)
            for line in lines_on_page:
                words_on_line = re.split(r'[^\w-]+', line)
                words_on_line = [morph.normal_forms(word)[0] for word in words_on_line]
                for word in self.words:
                    if morph.normal_forms(word)[0] in words_on_line:
                        count += 1
                        result_str += f'Страница №{k}: {line} <br>'
        if result_str == '':
            result_str = 'Запретные слова не обнаружены!'
        else:
            result_str = 'Обнаружены запретные слова! <br>' + result_str
        result_score = 1
        if count > self.min_count:
            if count <= self.max_count:
                result_score = 0.5
            else:
                result_score = 0
        return answer(True, result_str)