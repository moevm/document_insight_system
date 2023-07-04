
from ..base_check import BasePresCriterion, answer
from .find_def_sld import FindDefSld
from app.nlp.stemming import Stemming

import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

nltk.download('stopwords')
MORPH_ANALYZER = MorphAnalyzer()


class FindThemeInPres(BasePresCriterion):

    description = "Проверка упоминания темы в презентации"
    id = 'theme_in_pres_check'

    def __init__(self, file_info, limit = 40):
        super().__init__(file_info)
        self.check_conclusion = FindDefSld(file_info=file_info, key_slide="Заключение")
        self.limit = limit

    def check(self):

        stop_words = set(stopwords.words("russian"))

        self.check_conclusion.check()
        page_conclusion = ''.join((str(item) for item in self.check_conclusion.__getattribute__("found_idxs")))

        text_from_title = [slide for page, slide in enumerate(self.file.get_titles(), 1) if str(page) != page_conclusion]
        theme = ''.join(word for word in text_from_title[0])

        translator = str.maketrans('', '', string.punctuation)
        theme_without_punct = theme.translate(translator)
        words_in_theme = word_tokenize(theme_without_punct)
        lemma_theme = {MORPH_ANALYZER.parse(word)[0].normal_form for word in words_in_theme if word.lower() not in stop_words}


        text_from_slide = [slide for page, slide in enumerate(self.file.get_text_from_slides(), 1) if page > 1]
        string_from_text = ''.join(text_from_slide)

        text_without_punct = string_from_text.translate(translator)
        words_in_text = word_tokenize(text_without_punct)

        lemma_text = {MORPH_ANALYZER.parse(word)[0].normal_form for word in words_in_text if word.lower() not in stop_words}

        value_intersection = round(len(lemma_theme.intersection(lemma_text))*100//len(lemma_theme))

        if value_intersection == 0:
            return answer(False, f"Не пройдена! В презентации не упоминаются слова, завяленные в теме.")
        elif 1 < value_intersection < self.limit:
            return answer(False,
                          f"Не пройдена! Процент упоминания темы в вашей презентации ({value_intersection} %) ниже требуемого ({self.limit} %).")
        else:
            return answer(True, f'Пройдена! Процент упоминания темы в презентации: {value_intersection} %')
