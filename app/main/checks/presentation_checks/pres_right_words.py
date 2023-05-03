import re

from ..base_check import BasePresCriterion, answer


class PresRightWordsCheck(BasePresCriterion):
    description = "Проверка наличия определенных (правильных) слов в презентации"
    id = 'pres_right_words'

    def __init__(self, file_info, patterns=[]):
        super().__init__(file_info)
        self.patterns = dict.fromkeys(patterns, False)

    def check(self):
        for i, text_on_page in enumerate(self.file.get_text_from_slides()):
            if i == 0:
                continue  # skip title page
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
                          f'Не найдены слова, соответствующие следующим регулярным выражениям: <ul><li>{result_str}</ul>')
