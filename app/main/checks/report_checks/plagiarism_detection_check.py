from ..antiplagiarism.TextPreprocessing import TextProcessing
from ..antiplagiarism.compareTexts import compareTexts
from ..base_check import BaseReportCriterion, answer


class PlagiarismCheck(BaseReportCriterion):
    label = "Проверка на некорректные заимствования в тексте"
    description = "Тестовый критерий проверки на текстовые заимствования (плагиат) в отчёте"
    id = 'plagiarism_detection_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.corpus = []
        self.text_for_check = []

    def check(self):
        result_score = 1
        percent = 0
        for i in range(len(self.corpus)):
            for j in range(len(self.corpus)):
                if self.corpus[i] == self.corpus[j]:
                    continue
                suspect_text = self.corpus[i]["hashed_text"]
                # text_to_compare = TextProcessing(suspect_text).processText()
                # percent = compareTexts(self.text_for_check, text_to_compare)
                return answer(result_score,"Результат проверки на плагиат: {}% текста {} заимствовано "
                              "из {}".format(percent, self.corpus[i], self.corpus[j]))

    def get_texts(self):
        from ....db.db_methods import get_all_hashed_texts
        hashed_texts = get_all_hashed_texts()
        for i in range(len(hashed_texts)):
            self.corpus.append(hashed_texts["hashed_text"])

    def text_for_check(self):
        text = []
        for page_num, text_on_page in enumerate(self.file.pdf_file.get_text_on_page().values()):
            text.append(text_on_page)
            self.text_for_check.append(TextProcessing(text).processText())
