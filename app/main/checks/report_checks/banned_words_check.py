import re

from ..base_check import BaseReportCriterion, answer
from ..word_counts import normalize_phrase, phrase_counts
from .style_check_settings import StyleCheckSettings


class ReportBannedWordsCheck(BaseReportCriterion):
    label = "Проверка наличия запретных слов в тексте отчёта"
    _description = 'Запрещено упоминание определенных "опасных" слов'
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
        config = StyleCheckSettings.CONFIGS.get(self.config)
        if not isinstance(config, dict):
            raise ValueError(f'Неизвестная карта заголовков: {self.config}')
        settings = config.get(self.headers_main, config.get('any_header', {}))
        self.words = {normalize_phrase(word) for word in settings.get('banned_words', [])}
        self.warned_words = {normalize_phrase(word) for word in settings.get('warned_words', [])}
        self.min_count = settings.get('min_count_for_banned_words_check', 3)
        self.max_count = settings.get('max_count_for_banned_words_check', 6)

    def check(self):
        if not self.has_enough_pages():
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        result_str = f'<b>Запрещенные слова: {"; ".join(self.words)}</b><br>'
        banned_counter = {'words': self.words, 'detected_lines': {}, 'count': 0}
        warned_counter = {'words': self.warned_words, 'detected_lines': {}, 'count': 0}
        for k, v in self.file.pdf_file.get_text_on_page().items():
            lines_on_page = re.split(r'\n', v)
            for index, line in enumerate(lines_on_page):
                for counter in (banned_counter, warned_counter):
                    counts = phrase_counts(line, counter['words'])
                    count_banned_words = {word for word, count in counts.items() if count}
                    if count_banned_words:
                        counter['count'] += sum(counts.values())
                        if k not in counter['detected_lines'].keys():
                            counter['detected_lines'][k] = []
                        counter['detected_lines'][k].append(
                            f'Строка {index + 1}: {line} <b>[{"; ".join(count_banned_words)}]</b>'
                        )
        if len(banned_counter['detected_lines']):
            result_str += 'Обнаружены запретные слова! <br><br>'
            for k, _ in banned_counter['detected_lines'].items():
                result_str += f'Страница №{k}:<br>{"<br>".join(banned_counter['detected_lines'][k])}<br><br>'
        else:
            result_str = 'Пройдена!'

        if len(warned_counter['detected_lines']):
            result_str += (
                '<br><br>Обнаружены потенциально опасные слова (не влияют на результат проверки)!<br>'
                'Обратите внимание, что их использование возможно только в подтвержденных случаях:'
                f'{"; ".join(self.warned_words)}<br><br>'
            )
            for k, _ in warned_counter['detected_lines'].items():
                result_str += f'Страница №{k}:<br>{"<br>".join(warned_counter['detected_lines'][k])}<br><br>'

        result_score = 1
        if banned_counter['count'] > self.min_count:
            if banned_counter['count'] <= self.max_count:
                result_score = 0.5
            else:
                result_score = 0
        return answer(result_score, result_str)
