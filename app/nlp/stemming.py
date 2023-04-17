import itertools

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from pymorphy2 import MorphAnalyzer

nltk.download('stopwords')
nltk.download('punkt')

MORPH_ANALYZER = MorphAnalyzer()
TASKS = 'задачи:'


class Stemming:
    def __init__(self):
        self.sentences = []
        self.find_further_development = False
        self.filtered_docs = []
        self.further_dev_sentence = 'Не найдены'

    def get_sentences(self, string, flag):
        self.sentences = []
        find_title_tasks = False
        for sent in string.split('\n'):
            if flag and TASKS not in sent.lower() and not find_title_tasks:
                continue
            find_title_tasks = True
            for s in sent_tokenize(sent):
                self.sentences.append(s)
        return self.sentences

    def parse_text(self, string, flag):
        # morph = MorphAnalyzer()
        FURTHER_DEVELOPMENT = MORPH_ANALYZER.parse('дальнейшие'.lower())[0].normal_form
        FURTHER_IMPROVEMENTS = MORPH_ANALYZER.parse('улучшения'.lower())[0].normal_form
        self.sentences = []
        self.find_further_development = False
        self.filtered_docs = []
        stop_words = set(stopwords.words("russian"))
        filtered_doc = []
        self.get_sentences(string, flag)

        for sent in self.sentences:
            token_sent = [w.lower() for w in word_tokenize(sent) if w.lower() not in stop_words]
            for word in token_sent:
                w = MORPH_ANALYZER.parse(word)[0].normal_form
                filtered_doc.append(w)
                if w in [FURTHER_DEVELOPMENT, FURTHER_IMPROVEMENTS] and not flag:
                    self.find_further_development = True
                    self.further_dev_sentence = sent
            self.filtered_docs.append(filtered_doc)
            filtered_doc = []

    def get_filtered_docs(self, string, flag):
        self.parse_text(string, flag)
        return set(itertools.chain(*self.filtered_docs))

    def further_dev(self):
        return {'found_dev': self.find_further_development, 'dev_sentence': self.further_dev_sentence}
