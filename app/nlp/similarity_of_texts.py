import gensim
import numpy as np
from app.nlp.stemming import get_filtered_docs
import os
PATH = os.path.dirname(__file__) + '/' + 'workdir/'


def check_similarity(file1, file2):
    gen_docs = get_filtered_docs(file1, True)
    dictionary = gensim.corpora.Dictionary(gen_docs)
    corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]

    tf_idf = gensim.models.TfidfModel(corpus)
    sims = gensim.similarities.Similarity(PATH, tf_idf[corpus],
                                          num_features=len(dictionary))

    avg_sims = []

    gen_docs1 = get_filtered_docs(file2, False)

    for g in gen_docs1:
        query_doc_bow = dictionary.doc2bow(g)
        query_doc_tf_idf = tf_idf[query_doc_bow]
        sum_of_sims = (np.sum(sims[query_doc_tf_idf], dtype=np.float32))
        avg = sum_of_sims / len(gen_docs)
        avg_sims.append(avg)
    total_avg = np.sum(avg_sims, dtype=np.float)
    percentage_of_similarity = round(float(total_avg) * 100)
    return percentage_of_similarity
