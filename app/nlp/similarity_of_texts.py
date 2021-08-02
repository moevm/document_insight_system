from os import mkdir
from os.path import exists
from shutil import rmtree
import re
import gensim
import numpy as np

from app import server
from app.nlp.stemming import Stemming
from logging import getLogger
logger = getLogger('root')

PATH = server.UPLOAD_FOLDER + '/workdir/'


def check_similarity(string1, string2):
    try:
        if exists(PATH):
            rmtree(PATH)
        mkdir(PATH)

        stemming = Stemming()
        gen_docs = stemming.get_filtered_docs(string1, True)

        dictionary = gensim.corpora.Dictionary(gen_docs)
        corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]

        tf_idf = gensim.models.TfidfModel(corpus)
        sims = gensim.similarities.Similarity(PATH, tf_idf[corpus], num_features=len(dictionary))

        avg_sims = []


        gen_docs1 = stemming.get_filtered_docs(string2, False)
        further_dev = stemming.further_dev()
        base_conclusions = stemming.get_sentences(string2, False)
        ignore = re.compile('[0-9]+[.]?|Заключение|‹#›')
        clear_conclusions = [ch for ch in base_conclusions if not re.fullmatch(ignore, ch)]
        recognized_conclusions = [s for s in clear_conclusions if s != further_dev.get('dev_sentence')]


        for g in gen_docs1:
            query_doc_bow = dictionary.doc2bow(g)
            query_doc_tf_idf = tf_idf[query_doc_bow]
            sum_of_sims = (np.sum(sims[query_doc_tf_idf], dtype=np.float32))
            avg = sum_of_sims / len(gen_docs)
            avg_sims.append(avg)
        total_avg = np.sum(avg_sims, dtype=np.float)/len(gen_docs1)
        if total_avg > 1:
            total_avg = 1
        percentage_of_similarity = round(float(total_avg) * 100)

        if exists(PATH):
            rmtree(PATH)
        return percentage_of_similarity, further_dev, recognized_conclusions
    except OSError:
        if exists(PATH):
            rmtree(PATH)
        logger.info("Проблема с директорией ", PATH)
        return -1
