from pymorphy2 import MorphAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

TASKS = 'задачи:'


def get_filtered_docs(file, flag):
    morph = MorphAnalyzer()
    stop_words = stopwords.words("russian")
    sentences = []
    filtered_docs = []
    filtered_doc = []
    find_title_tasks = False
    with open(file) as f:
        for sent in f:
            if flag and not TASKS in sent.lower() and not find_title_tasks:
                continue
            find_title_tasks = True
            for s in sent_tokenize(sent):
                sentences.append(s)
    for sent in sentences:
        for word in word_tokenize(sent):
            if word.isalpha():
                word = word.lower()
                if word not in stop_words:
                    filtered_doc.append(morph.parse(word)[0].normal_form)
        filtered_docs.append(filtered_doc)
        filtered_doc = []
    return filtered_docs
