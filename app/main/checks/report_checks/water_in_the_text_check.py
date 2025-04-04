import re
from collections import Counter
from ..base_check import BaseReportCriterion, answer, morph
from .watery_phrase_settings import WateryPhrase

class WaterInTheTextCheck(BaseReportCriterion):
    label = "Проверка объема воды в тексте"
    description = ''
    id = 'water_in_the_text_check'

    def __init__(self, file_info, watery_phrase_threshold=0.3, long_sentence_threshold=0.3, meaningful_word_threshold=0.6):
        super().__init__(file_info)
        self.chapters = []
        self.watery_phrase = None
        self.watery_words = None
        self.watery_phrase_threshold = watery_phrase_threshold
        self.long_sentence_threshold = long_sentence_threshold
        self.meaningful_word_threshold = meaningful_word_threshold

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        self.watery_phrase = WateryPhrase.INTRODUCTORY_PHRASE
        self.watery_words = WateryPhrase.SERVICE_WORDS + WateryPhrase.ABSTRACT_WORDS
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        result_str = ""
        for chapter in self.chapters:
            if 'список использованных источников' in chapter['text'].lower():
                break
            text = self.get_chapter_text(chapter)
            words = self.get_words(text)
            if self.watery_phrase_density(text, words) > self.watery_phrase_threshold:
                result_str += f"В Разделе '{chapter['text']}' содержится более {self.watery_phrase_threshold*100}% 'водянистых' фраз.<br>"

            if self.long_sentences_density(text) > self.long_sentence_threshold:
                result_str += f"В разделе '{chapter['text']}' более {self.long_sentence_threshold*100}% предложений длиннее 20 слов.<br>"

            if self.meaningful_word_density(words) < self.meaningful_word_threshold:
                result_str += f"В разделе '{chapter['text']}' доля значимых слов составляет менее {self.meaningful_word_threshold*100}% от общего количества слов.<br>"
        if not result_str:
            return answer(True, "Пройдена!")
        return answer(False, result_str)

    def get_chapter_text(self, chapter):
        chapter_text = ""
        for child in chapter['child']:
            chapter_text += " " + child['text']
        return chapter_text

    def get_words(self, text):
        cleaned_text = re.sub(r'\s+', ' ', text)
        return re.findall(r'\b\w+(?:-\w+)*\b', re.sub(r'[^а-яА-ЯёЁ\s-]', '', cleaned_text.lower()))

    def watery_phrase_density(self, text, words):
        watery_phrase_count = sum(text.lower().count(phrase) for phrase in self.watery_phrase)
        watery_phrase_count += sum(word in self.watery_words for word in words)
        if len(words) == 0:
            return 0
        return watery_phrase_count / len(words) 

    def long_sentences_density(self, text):
        sentences = re.split(r'[.!?]', text)
        long_sentences_count = sum(len(sentence.split()) > 20 for sentence in sentences)
        total_sentences = len(sentences)
        if total_sentences <= 3 :
            return 0
        return long_sentences_count / total_sentences 

    def meaningful_word_density(self, words):
        meaningful_words = [
            word for word in words
            if morph.parse(word)[0].tag.POS in {'NOUN', 'VERB', 'ADJF', 'ADJS','INFN'}
        ]
        if len(words) == 0:
            return 1
        return len(meaningful_words) / len(words)