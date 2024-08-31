import re
import  string

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
from ..base_check import BaseReportCriterion, answer


MORPH_ANALYZER = MorphAnalyzer()

class KeyWordsReportCheck(BaseReportCriterion):
    label = 'Проверка наличия раздела "Ключевые слова" и упоминание их в тексте'
    description = 'Раздел идет сразу после названия работы и содержит не менее трех ключевых слов. Слова упоминаются в тексте'
    id = 'Key_words_report_check'

    def __init__(self, file_info, min_key_words = 3):
        super().__init__(file_info)
        self.min_key_words = min_key_words
        self.chapters = []
        self.text_par = []
        self.lemme_list = []

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        key_words_chapter = self.file.paragraphs[1].lower()
        if 'ключевые слова' not in key_words_chapter:
            return answer(False, 'Раздел "Ключевые слова" не найден')
        cleaned_str = re.sub(r'<[^>]*>', '', key_words_chapter)
        final_str = cleaned_str.replace('ключевые слова', '').replace(':','')
        key_words_result = [word.strip() for word in final_str.split(',')]
        if len(key_words_result) < self.min_key_words:
            return answer(False, f'Не пройдена! Количество ключевых слов должно быть не менее {self.min_key_words}')
        stop_words = set(stopwords.words("russian"))
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        for intro in self.chapters:
            header = intro["text"].lower()
            if header not in ['аннотация', "ключевые слова"]:
                self.intro = intro
                for intro_par in self.intro['child']:
                    par = intro_par['text'].lower()
                    self.text_par.append(par)
        for phrase in key_words_result:
            words = word_tokenize(phrase)
            words_lemma = [MORPH_ANALYZER.parse(w)[0].normal_form for w in words if w.lower() not in stop_words]
            phrase_lemma = ' '.join(words_lemma)
            self.lemme_list.append(phrase)
            for text in self.text_par:
                cleaned_text = re.sub(r'<[^>]*>', '', text)
                translator = str.maketrans('', '', string.punctuation)
                text_without_punct = cleaned_text.translate(translator)
                word_in_text = word_tokenize(text_without_punct)
                lemma_text = [MORPH_ANALYZER.parse(w)[0].normal_form for w in word_in_text if w.lower() not in stop_words]
                lemma_text_str = ' '.join(lemma_text)
                if phrase_lemma in lemma_text_str:
                    del self.lemme_list[-1]
                    break

        if self.lemme_list:
            return answer(False, f"Не пройдена! В тексте не найдены следующие ключевые слова: «{'», «'.join(self.lemme_list)}»")
        else:
            return answer(True, f'Пройдена!')
