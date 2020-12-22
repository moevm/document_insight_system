import nltk

nltk.download('stopwords')
nltk.download('punkt')

from pymorphy2 import MorphAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

TASKS = 'задачи:'
FURTHER_DEVELOPMENT = 'дальнейшие'


class Stemming:
    def __init__(self):
        self.sentences = []
        self.find_further_development = False
        self.filtered_docs = []

    def parse_text(self, string, flag):
        morph = MorphAnalyzer()
        stop_words = stopwords.words("russian")
        filtered_doc = []
        find_title_tasks = False

        for sent in string.split('\n'):
            if flag and TASKS not in sent.lower() and not find_title_tasks:
                continue
            find_title_tasks = True
            for s in sent_tokenize(sent):
                self.sentences.append(s)
        for sent in self.sentences:
            for word in word_tokenize(sent):
                if word.isalpha():
                    word = word.lower()
                    if word not in stop_words:
                        w = morph.parse(word)[0].normal_form
                        filtered_doc.append(w)
                        if w == morph.parse(FURTHER_DEVELOPMENT.lower())[0].normal_form and flag == False:
                            self.find_further_development = True
            self.filtered_docs.append(filtered_doc)
            filtered_doc = []

    def get_filtered_docs(self, string, flag):
        self.parse_text(string, flag)
        return self.filtered_docs

    def is_find_further_development_on_slide(self):
        return self.find_further_development
