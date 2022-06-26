import re
from ..base_check import BaseCheck, answer


class ReportRightWordsCheck(BaseCheck):
    def __init__(self, file, patterns = []):
        super().__init__(file)
        self.patterns = dict.fromkeys(patterns, False)

    def check(self):
        for text_on_page in self.file.pdf_file.get_text_on_page().values():
            lower_text = text_on_page.lower()
            for pattern in self.patterns:
                if re.search(pattern, lower_text):
                    self.patterns[pattern] = True
        result_score = 0
        if all(value == True for value in self.patterns.values()):
            result_score = 1
        if result_score:
            return answer(result_score, "Все слова обнаружены в тексте!")
        else:
            result_str = '; '.join([k for k, v in self.patterns.items() if not v])
            return answer(result_score, f'Не найдены слова, соответствующие следующим регулярным выражениям: {result_str}')
