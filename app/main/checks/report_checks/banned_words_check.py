import re

from ..base_check import BaseReportCriterion, answer, morph


class ReportBannedWordsCheck(BaseReportCriterion):
    description = "Проверка наличия запретных слов в тексте отчёта"
    id = 'banned_words_check'

    def __init__(self, file_info, words=["мы"], min_count=3, max_count=6):
        super().__init__(file_info)
        self.words = [morph.normal_forms(word)[0] for word in words]
        self.min_count = min_count
        self.max_count = max_count

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        detected_lines = {}
        result_str = f'<b>Запрещенные слова: {"; ".join(self.words)}</b><br>'
        count = 0
        for k, v in self.file.pdf_file.get_text_on_page().items():
            lines_on_page = re.split(r'\n', v)
            for index, line in enumerate(lines_on_page):
                words_on_line = re.split(r'[^\w-]+', line)
                words_on_line = [morph.normal_forms(word)[0] for word in words_on_line]
                count_banned_words = set(words_on_line).intersection(self.words)
                if count_banned_words:
                    count += len(count_banned_words)
                    if k not in detected_lines.keys():
                        detected_lines[k] = []
                    detected_lines[k].append(f'Строка {index + 1}: {line} <b>[{"; ".join(count_banned_words)}]</b>')
        if len(detected_lines):
            result_str += 'Обнаружены запретные слова! <br><br>'
            for k, v in detected_lines.items():
                result_str += f'Страница №{k}:<br>{"<br>".join(detected_lines[k])}<br><br>'
        else:
            result_str = 'Пройдена!'
        result_score = 1
        if count > self.min_count:
            if count <= self.max_count:
                result_score = 0.5
            else:
                result_score = 0
        return answer(result_score, result_str)
