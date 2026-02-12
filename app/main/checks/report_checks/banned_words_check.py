import re
from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer, morph


class ReportBannedWordsCheck(BaseReportCriterion):
    label = "Проверка наличия запретных слов в тексте отчёта"
    description = 'Запрещено упоминание определенных "опасных" слов'
    id = 'banned_words_check'

    def __init__(self, file_info, headers_map=None):
        super().__init__(file_info)
        self.words = []
        self.warned_words = []
        self.min_count = 0
        self.max_count = 0
        if headers_map:
            self.config = headers_map
        else:
            self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'

    def late_init(self):
        self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
        if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config):
            self.words = {morph.normal_forms(word)[0] for word in StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['banned_words']}
            self.warned_words = {morph.normal_forms(word)[0] for word in StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['warned_words']}
            self.min_count = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['min_count_for_banned_words_check']
            self.max_count = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['max_count_for_banned_words_check']
        else:
            if 'any_header' in StyleCheckSettings.CONFIGS.get(self.config):
                self.words = {morph.normal_forms(word)[0] for word in StyleCheckSettings.CONFIGS.get(self.config)['any_header']['banned_words']}
                self.warned_words = {morph.normal_forms(word)[0] for word in StyleCheckSettings.CONFIGS.get(self.config)['any_header']['warned_words']}
                self.min_count = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['min_count_for_banned_words_check']
                self.max_count = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['max_count_for_banned_words_check']

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        result_str = f'<b>Запрещенные слова: {"; ".join(self.words)}</b><br>'
        banned_counter = {'words': self.words, 'detected_lines': {}, 'count': 0}
        warned_counter = {'words': self.warned_words,'detected_lines': {}, 'count': 0}
        for k, v in self.file.pdf_file.get_text_on_page().items():
            lines_on_page = re.split(r'\n', v)
            for index, line in enumerate(lines_on_page):
                words_on_line = {morph.normal_forms(word)[0] for word in re.split(r'[^\w-]+', line)}
                for counter in (banned_counter, warned_counter):
                    count_banned_words = words_on_line.intersection(counter['words'])
                    if count_banned_words:
                        counter['count'] += len(count_banned_words)
                        if k not in counter['detected_lines'].keys():
                            counter['detected_lines'][k] = []
                        counter['detected_lines'][k].append(f'Строка {index + 1}: {line} <b>[{"; ".join(count_banned_words)}]</b>')
        if len(banned_counter['detected_lines']):
            result_str += 'Обнаружены запретные слова! <br><br>'
            for k, v in banned_counter['detected_lines'].items():
                result_str += f'Страница №{k}:<br>{"<br>".join(banned_counter['detected_lines'][k])}<br><br>'
        else:
            result_str = 'Пройдена!'
        
        if len(warned_counter['detected_lines']):
            result_str += f'<br><br>Обнаружены потенциально опасные слова (не влияют на результат проверки)!<br>Обратите внимание, что их использование возможно только в подтвержденных случаях: {"; ".join(self.warned_words)}<br><br>'
            for k, v in warned_counter['detected_lines'].items():
                result_str += f'Страница №{k}:<br>{"<br>".join(warned_counter['detected_lines'][k])}<br><br>'

        result_score = 1
        if banned_counter['count'] > self.min_count:
            if banned_counter['count'] <= self.max_count:
                result_score = 0.5
            else:
                result_score = 0
        return answer(result_score, result_str)
