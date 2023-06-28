import re

from ..base_check import BaseReportCriterion, answer


class ReportRightWordsCheck(BaseReportCriterion):
    description = "Проверка наличия определенных (правильных) слов в тексте отчёта"
    id = 'right_words_check'

    def __init__(self, file_info, patterns=["цель"]):
        super().__init__(file_info)
        self.patterns = dict.fromkeys(patterns, False)

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        for text_on_page in self.file.pdf_file.get_text_on_page().values():
            lower_text = text_on_page.lower()
            for pattern in self.patterns:
                if re.search(pattern, lower_text):
                    self.patterns[pattern] = True
        result_score = 0
        if all(value == True for value in self.patterns.values()):
            result_score = 1
        if result_score:
            return answer(result_score, "Пройдена!")
        else:
            result_str = '</li><li>'.join([k for k, v in self.patterns.items() if not v])
            return answer(result_score,
                          f'Не найдены слова, соответствующие следующим регулярным выражениям: '
                          f'<ul><li>{result_str}</ul>')
