import nltk
nltk.download('stopwords')
nltk.download('punkt')

from pymorphy2 import MorphAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords


TASKS = 'задачи:'
FURTHER_DEVELOPMENT = 'дальнейшие'


def get_filtered_docs(string, flag):
    morph = MorphAnalyzer()
    stop_words = stopwords.words("russian")
    sentences = []
    filtered_docs = []
    filtered_doc = []
    find_title_tasks = False
    find_further_development = False
    for sent in string.split('\n'):
        if flag and TASKS not in sent.lower() and not find_title_tasks:
            continue
        find_title_tasks = True
        for s in sent_tokenize(sent):
            sentences.append(s)
    for sent in sentences:
        for word in word_tokenize(sent):
            if word.isalpha():
                word = word.lower()
                if word not in stop_words:
                    w = morph.parse(word)[0].normal_form
                    filtered_doc.append(w)
                    if w == morph.parse(FURTHER_DEVELOPMENT.lower())[0].normal_form and flag == False:
                        find_further_development = True
        filtered_docs.append(filtered_doc)
        filtered_doc = []
    return [filtered_docs, find_further_development]
