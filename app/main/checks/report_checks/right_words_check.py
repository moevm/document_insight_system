import re
# import nltk
from ..base_check import BaseCheck, answer


# nltk.download('punkt')

class ReportRightWordsCheck(BaseCheck):
    def __init__(self, file, words):
        super().__init__(file)
        self.words = dict.fromkeys(words, False)

    def check(self):
        for text in self.file.paragraphs:
            words = re.split(r'[^/w-]', text.paragraph_text)
            # words = nltk.word_tokenize(text)
            for word in words:
                for k, v in self.words.items():
                    if re.match(k, word):
                        self.words[k] = True
        result_score = 0
        if all(value == True for value in self.words.values()):
            result_score = 1
        return answer(True, "Пройдена!")
