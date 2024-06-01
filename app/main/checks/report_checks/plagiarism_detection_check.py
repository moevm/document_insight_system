from ..antiplagiarism.TextPreprocessing import TextProcessing
from ..antiplagiarism.compareTexts import compareTexts
from ..base_check import BaseReportCriterion, answer


class PlagiarismCheck(BaseReportCriterion):
    label = "Проверка на некорректные заимствования в тексте"
    description = "Тестовый критерий проверки на текстовые заимствования (плагиат) в отчёте"
    id = 'plagiarism_detection_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.corpus = {}
        self.text_for_check = ""

    # def check(self):
    #     for i in range(len(self.corpus)):
    #         check_text = self.text_for_check
    #         Text1 = TextProcessing(check_text.read()).processText()
    #         for j in range(len(self.corpus)):
    #             if self.corpus[i] == self.corpus[j]:
    #                 continue
    #             suspect_text = self.corpus[i]["enabled_checks"]["parsed_text"]
    #             Text2 = TextProcessing(suspect_text.read()).processText()
    #             percent = compareTexts(Text1, Text2)
    #             result_score = 1
    #             return answer(result_score, "Результат проверки на плагиат: "
    #                                 "{}% текста {} заимствовано из {}".format(percent, self.corpus[i], self.corpus[j]))

    def get_texts(self):
        from ....db.db_methods import get_all_checks
        all_checks = get_all_checks()
        for i in range(len(all_checks)):
            enabled_checks = all_checks[i]["enabled_checks"]
            # for j in range(len(enabled_checks)):
            #     self.corpus.update(i+1, enabled_checks[j]["parsed_text"])

    def text_for_check(self):
        for page_num, text_on_page in enumerate(self.file.pdf_file.get_text_on_page().values()):
            self.text_for_check += text_on_page
