import re
from ..base_check import BaseReportCriterion, answer, morph


class ReportBannedWordsCheck(BaseReportCriterion):
    description = "Проверка наличия запретных слов в тексте отчёта"
    id = 'banned_words_check'

    def __init__(self, file_info, words = [], min_count = 3, max_count = 6):
        super().__init__(file_info)
        self.words = [morph.normal_forms(word)[0] for word in words]
        self.min_count = min_count
        self.max_count = max_count

    def check(self):
        result_str = ''
        count = 0
        for k, v in self.file.pdf_file.get_text_on_page().items():
            lines_on_page = re.split(r'\n', v)
            for line in lines_on_page:
                words_on_line = re.split(r'[^\w-]+', line)
                words_on_line = [morph.normal_forms(word)[0] for word in words_on_line]
                count_banned_words = set(words_on_line).intersection(self.words)
                if count_banned_words:
                    count += len(count_banned_words)
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
        return answer(result_score, result_str)