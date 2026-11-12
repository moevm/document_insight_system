import re

from app.nlp.tokenization import content_lemmas

from ..base_check import BaseReportCriterion, answer


class FindThemeInReport(BaseReportCriterion):
    label = 'Проверка упоминания темы в отчёте'
    _description = 'Слова темы упоминаются в основном тексте отчёта.'
    id = 'theme_in_report_check'

    def __init__(self, file_info, limit=40, theme=None):
        super().__init__(file_info)
        self.limit = limit
        self.theme = theme
        if not 0 < limit <= 100:
            raise ValueError('limit должен быть в пределах (0; 100].')

    def find_theme(self):
        if self.theme is not None:
            return set(content_lemmas(self.theme))
        first_page = next(iter(self.file.pdf_file.get_text_on_page().values()), '')
        match = re.search(r'тема\s*[:—-]?\s*(.+?)(?=\n|\bстудент(?:ка)?\b|$)', first_page, re.I)
        theme = match.group(1) if match else (self.file.get_main_headers('VKR') if self.is_markdown else '')
        return set(content_lemmas(theme))

    def check(self):
        theme = self.find_theme()
        if not theme:
            return answer(False, 'Не удалось определить тему отчёта.')
        text = []
        for chapter in self.file.make_chapters(self.file_type['report_type']):
            title = chapter['text'].strip().lower()
            if title.startswith('приложение') or 'список использованных источников' in title:
                break
            if title in ('введение', 'заключение', 'определения, обозначения и сокращения'):
                continue
            text.extend(child['text'] for child in chapter['child'])
        percent = round(len(theme & set(content_lemmas(' '.join(text)))) * 100 / len(theme))
        return answer(
            min(percent / self.limit, 1), f'Процент упоминания темы в отчёте: {percent}%; требуется {self.limit}%.'
        )
