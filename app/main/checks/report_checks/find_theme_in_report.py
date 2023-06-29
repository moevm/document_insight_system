import re
import string

from ..base_check import BaseReportCriterion, answer
# from .find_def_sld import FindDefSld
# from app.nlp.stemming import Stemming
from ...reports.pdf_document.pdf_document_manager import PdfDocumentManager
import pdfplumber
from ...reports.docx_uploader import DocxUploader

import  string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

nltk.download('stopwords')
MORPH_ANALYZER = MorphAnalyzer()


class FindThemeInReport(BaseReportCriterion):

    description = "Проверка упоминания темы в отчете"
    id = 'theme_in_report_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.intro = {}
        self.chapters = []
        self.text_par = []
        self.full_text = set()

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
        for i in self.text_par:
            translator = str.maketrans('', '', string.punctuation)
            theme_without_punct = i.translate(translator)
            word_in_text = word_tokenize(theme_without_punct)
            lemma_text = {MORPH_ANALYZER.parse(w)[0].normal_form for w in word_in_text if w.lower() not in stop_words}
            self.full_text.update(lemma_text)

        intersection = lemma_theme.intersection(self.full_text)
        int_pr = round(len(intersection)*100//len(lemma_theme))

        return answer(True, f'{lemma_theme} {intersection} hhh {int_pr}')






    def find_theme(self):
        stop_words = set(stopwords.words("russian"))
        lemma_theme = []
        for key, text_on_page in self.file.pdf_file.get_text_on_page().items():
            if key == 1:
                lower_text = text_on_page.lower()
                text_without_punct = lower_text.translate(str.maketrans('', '', string.punctuation))
                list_full = text_without_punct.split()
                start = list_full.index('тема') + 1
                end = list_full.index('студент')
                list_theme = list_full[start:end]
                lemma_theme = {MORPH_ANALYZER.parse(word)[0].normal_form for word in list_theme if
                                word not in stop_words}
            return lemma_theme





        # full_text_pre = self.file.pdf_file.text_on_page
        # full_text = ''.jo
        # start_text = full_text.index['1.']
        # end_text = full_text.index['ЗАКЛЮЧЕНИЕ']
        # text_for_analys = full_text[start_text:end_text]
        # lemma_text = {MORPH_ANALYZER.parse(word)[0].normal_form for word in text_for_analys if word not in stop_words}

        # for text_on_page in self.file.pdf_file.get_text_on_page().values():
        #
        #     lower_text = text_on_page.lower()
        #     text_without_punct = lower_text.translate(str.maketrans('', '', string.punctuation))
        #     list_full = text_without_punct.split()
        #     start = list_full.index('тема')
        #     end = list_full.index('студент')
        #     list_theme = list_full[start:end]
        #     lemma_theme = ({MORPH_ANALYZER.parse(word)[0].normal_form for word in list_theme if
        #                    word not in stop_words})






# class FindThemeInReport(BaseReportCriterion):
#
#     description = "Проверка упоминания темы в отчете"
#     id = 'theme_in_report_check'
#
#     def __init__(self, file_info):
#         super().__init__(file_info)
#         self.check_conclusion = FindDefSld(file_info=file_info, key_slide="Заключение")
#
#     def check(self):
#
#         stop_words = set(stopwords.words("russian"))
#
#         self.check_conclusion.check()
#         page_conclusion = ''.join((str(item) for item in self.check_conclusion.__getattribute__("found_idxs")))
#
#         text_from_title = [slide for page, slide in enumerate(self.file.get_titles(), 1) if str(page) != page_conclusion]
#         theme = ''.join(word for word in text_from_title[0])
#
#         translator = str.maketrans('', '', string.punctuation)
#         theme_without_punct = theme.translate(translator)
#         words_in_theme = word_tokenize(theme_without_punct)
#         # for word in words_in_theme:
#         lemma_theme = {MORPH_ANALYZER.parse(word)[0].normal_form for word in words_in_theme if word.lower() not in stop_words}
#
#
#         text_from_slide = [slide for page, slide in enumerate(self.file.get_text_from_slides(), 1) if page > 1]
#         string_from_text = ''.join(text_from_slide)
#
#         text_without_punct = string_from_text.translate(translator)
#         words_in_text = word_tokenize(text_without_punct)
#
#         lemma_text = {MORPH_ANALYZER.parse(word)[0].normal_form for word in words_in_text if word.lower() not in stop_words}
#
#         intersection = round(len(lemma_theme.intersection(lemma_text))//len(lemma_theme))*100
#
#         if intersection == 0:
#             return answer(False, f"Не пройдена! {intersection}")
#         elif 1 < intersection < 40:
#             return answer(False, f"Обратите внимание! {intersection} %")
#         else:
#             return answer (True, f'Пройдена! {intersection} %')
