import re
from ..base_check import BaseCheck, answer


class ReportRightWordsCheck(BaseCheck):
    def __init__(self, file, words = []):
        super().__init__(file)
        self.words = dict.fromkeys(words, False)

    def check(self):
        for text_on_page in self.file.pdf_file.get_text_on_page().values():
            words = re.split(r'[^/w-]', text_on_page)
            for word in words:
                for k in self.words.keys():
                    if re.match(k, word):
                        self.words[k] = True
        result_score = 0
        if all(value == True for value in self.words.values()):
            result_score = 1
        if result_score:
            return answer(result_score, "Все слова обнаружены в тексте!")
        else:
            result_str = '; '.join([k for k, v in self.words.items() if not v])
            return answer(result_score, f'Не найдены слова, соответствующие следующим регулярным выражениям: {result_str}')
