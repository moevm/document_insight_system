import re

from ..base_check import BaseReportCriterion, answer


class BannedWordsInLiteratureCheck(BaseReportCriterion):
    label = "Проверка наличия запрещенных слов в списке литературы"
    _description = 'Проверка наличия запрещенных слов, например: '
    id = 'banned_words_in_literature'
    banned_words = ["habr", "medium", "stackoverflow", "sky.pro", "geeksforgeeks", "wikipedia"]

    def __init__(self, file_info, banned_words=None):
        super().__init__(file_info)
        self.banned_words = list(dict.fromkeys([*type(self).banned_words, *(banned_words or [])]))
        self.headers_page = 1
        self.literature_header = []
        self.name_pattern = r'список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы)'

    def late_init_vkr(self):
        self.literature_header = self.file.find_literature_vkr(self.file_type['report_type'])
        # self.headers_page = self.file.find_header_page(self.file_type['report_type'])
        self.lit_page = self.file.find_literature_page(self.file_type['report_type'])

    def check(self):
        header = self.file.find_literature_vkr(self.file_type['report_type'])
        if not header:
            return answer(False, 'Нет списка использованных источников / списка литературы.')
        if not header['child']:
            return answer(False, 'Не найдено ни одного источника.')
        errors = []
        for index, child in enumerate(header['child'], 1):
            text = child['text'].lower()
            found = [
                word
                for word in self.banned_words
                if re.search(r'(?<![\w])' + re.escape(word.lower()) + r'(?![\w])', text)
            ]
            if found:
                errors.append(f'Источник {index}: ' + ', '.join(found))
        return answer(not errors, '<br>'.join(errors) or 'Пройдена!')

    @classmethod
    def description(cls, pack: str | None = None):
        return cls._description + ','.join(cls.banned_words)
