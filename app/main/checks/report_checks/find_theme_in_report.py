import re
import string

from ..base_check import BaseReportCriterion, answer

import  string
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer


MORPH_ANALYZER = MorphAnalyzer()


class FindThemeInReport(BaseReportCriterion):
    label = "Проверка упоминания темы в отчете"
    description = "Проверка упоминания темы в отчете"
    id = 'theme_in_report_check'

    def __init__(self, file_info, limit = 40):
        super().__init__(file_info)
        self.intro = {}
        self.chapters = []
        self.text_par = []
        self.full_text = set()
        self.limit = limit

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        stop_words = set(stopwords.words("russian"))
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")

        self.late_init()
        for intro in self.chapters:
            header = intro["text"].lower()
            if header not in ['заключение', "введение", "список использованных источников", "условные обозначения"]:
                self.intro = intro
                for intro_par in self.intro['child']:
                    par = intro_par['text'].lower()
                    self.text_par.append(par)
        lemma_theme = self.find_theme()

        for text in self.text_par:
            translator = str.maketrans('', '', string.punctuation)
            theme_without_punct = text.translate(translator)
            word_in_text = word_tokenize(theme_without_punct)
            lemma_text = {MORPH_ANALYZER.parse(w)[0].normal_form for w in word_in_text if w.lower() not in stop_words}
            self.full_text.update(lemma_text)

        intersection = lemma_theme.intersection(self.full_text)
        value_intersection = round(len(intersection)*100//len(lemma_theme))
        if value_intersection == 0:
            return answer(False, "Не пройдена! В отчете не упоминаются слова, заявленные в теме отчета.")
        elif value_intersection < self.limit:
            return answer(
                          round(value_intersection/self.limit, 1),
                          f"Частично пройдена! Процент упоминания темы в вашем отчете ({value_intersection} %) ниже требуемого ({self.limit} %)."
            )
        else:
            return answer (True, f'Пройдена! Процент упоминания темы в отчете: {value_intersection} %.')

    def find_theme(self):
        stop_words = set(stopwords.words("russian"))
        lemma_theme = []
        for key, text_on_page in self.file.pdf_file.get_text_on_page().items():
            if key == 1:
                lower_text = text_on_page.lower()
                text_without_punct = lower_text.translate(str.maketrans('', '', string.punctuation))
                list_full = tuple(text_without_punct.split())
                start, end = 0, len(list_full)
                for index, value in enumerate(list_full):
                    if value == "тема":
                        start = index + 1
                    elif value in {"студент", "студентка"}:
                        end = index
                list_theme = list_full[start:end]
                lemma_theme = {MORPH_ANALYZER.parse(word)[0].normal_form for word in list_theme if
                                word not in stop_words}
            return lemma_theme