
from ..base_check import BasePresCriterion, answer
from .find_def_sld import FindDefSld
from app.nlp.stemming import Stemming

import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer


MORPH_ANALYZER = MorphAnalyzer()


class FindThemeInPres(BasePresCriterion):
    label = "Проверка упоминания темы в заголовках презентации"
    description = """Проверка упоминания темы в заголовках презентации, не включая титульный слайд, слайды "Цели и задачи", "Заключение" """
    id = 'theme_in_pres_check'

    def __init__(self, file_info, skip_slides_nums=(1,), skip_slides_titles=("Заключение",), limit=60):
        super().__init__(file_info)
        self.skip_slides_title = skip_slides_titles
        slides = []
        for title in self.skip_slides_title:
            find_sld = FindDefSld(file_info=file_info, key_slide=title)
            find_sld.check()
            slides.extend(find_sld.found_idxs)
        self.skip_slides = [
            *skip_slides_nums,
            *slides
        ]        
        self.limit = limit

    def check(self):
        stop_words = set(stopwords.words("russian"))

        text_from_title = [slide for page, slide in enumerate(self.file.get_titles(), 1) if page not in self.skip_slides]
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
            return answer(False, "Не пройдена! В презентации не упоминаются слова, завяленные в теме.")
        elif value_intersection < self.limit:
            return answer(
                round(value_intersection / self.limit, 1),
                f"Частично пройдена! Процент упоминания темы в вашей презентации ({value_intersection} %) ниже требуемого ({self.limit} %)."
            )
        else:
            return answer(True, f'Пройдена! Процент упоминания темы в презентации: {value_intersection} %')
