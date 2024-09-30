import re
from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer, morph


class ReportBannedWordsCheck(BaseReportCriterion):
    label = "Проверка наличия запретных слов в тексте отчёта"
    description = 'Запрещено упоминание слова "мы" (если не указано другое)'
    id = 'banned_words_check'

    def __init__(self, file_info, headers_map=None):
        super().__init__(file_info)
        self.words = []
        self.min_count = 0
        self.max_count = 0
        if headers_map:
            self.config = headers_map
        else:
            self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'

    def late_init(self):
        self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
        if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config):
            self.words = [morph.normal_forms(word)[0] for word in StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['banned_words']]
            self.min_count = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['min_count_for_banned_words_check']
            self.max_count = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['max_count_for_banned_words_check']
        else:
            if 'any_header' in StyleCheckSettings.CONFIGS.get(self.config):
                self.words = [morph.normal_forms(word)[0] for word in StyleCheckSettings.CONFIGS.get(self.config)['any_header']['banned_words']]
                self.min_count = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['min_count_for_banned_words_check']
                self.max_count = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['max_count_for_banned_words_check']

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        detected_lines = {}
        result_str = f'<b>Запрещенные слова: {"; ".join(self.words)}</b><br>'
        count = 0
        for k, v in self.file.pdf_file.get_text_on_page().items():
            lines_on_page = (re.split(r'\n', v))
            lines_on_page = [line for line in lines_on_page if line.strip()]
            for index, line in enumerate(lines_on_page):
                words_on_line = re.split(r'[^\w-]+', line)
                words_on_line = [(morph.normal_forms(word)[0]).lower() for word in words_on_line if word]
                count_banned_words = set(words_on_line).intersection(set(self.words))
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
