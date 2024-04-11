from collections import defaultdict

import nltk
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.util import ngrams
import string


class NLPProcessor:
    def __init__(self, language='russian'):
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words(language))
        self.stemmer = SnowballStemmer(language)

    def preprocessing(self, text):
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word.lower() not in self.stop_words]
        return [self.stemmer.stem(token) for token in tokens]

    def get_ngrams(self, tokens, n=2):
        result = []
        for i in range(n):
            n_grams = ngrams(tokens, i + 1)
            result.extend([' '.join(grams) for grams in n_grams])
        return result

    def get_bag_of_n_gramms(self, corpus):
        new_corpus = []
        for item in corpus:
            for n_gramm in item:
                new_corpus.append(n_gramm)
        index_word = {}
        i = 0
        for word in new_corpus:
            if word in index_word.keys():
                continue
            index_word[word] = i
            i += 1
        return index_word

    def get_vector_by_BOW(self, bag_of_ngramms, doc, docs):
        def tf(word, doc):
            return doc.count(word) / len(doc)

        def idf(word, docs):
            word_in_docs = 0
            for item in docs:
                if word in item:
                    word_in_docs += 1
            return np.log10(len(docs) / (word_in_docs + 1))

        def tf_idf(word, doc, docs):
            return tf(word, doc) * idf(word, docs)

        count_dict = defaultdict(int)
        vec = np.zeros(len(bag_of_ngramms))
        for word in doc:
            count_dict[word] += tf_idf(word, doc, docs)

        for key, item in count_dict.items():
            vec[bag_of_ngramms[key]] = item
        return vec

    def cosine_similarity(self, vector1, vector2):
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)
        dot_product = np.dot(vector1, vector2)
        if norm1 == 0.0 or norm2 == 0.0:
            return 0
        cosine_sim = dot_product / (norm1 * norm2)
        return cosine_sim

    def calculate_cosine_similarity(self, goal, texts: dict):
        if not (goal or texts):
            return
        corpus = []
        text1_n_grams = self.get_ngrams(self.preprocessing(goal))
        text2_n_grams = {}
        for chapter in texts.keys():
            text2_n_grams[chapter] = self.get_ngrams(self.preprocessing(texts[chapter]))
        corpus.append(text1_n_grams)
        corpus.extend(text2_n_grams.values())
        bag_of_n_grams = self.get_bag_of_n_gramms(corpus)
        goal_vector = self.get_vector_by_BOW(bag_of_n_grams, text1_n_grams, corpus)
        text_vectors = {}
        for chapter, text in text2_n_grams.items():
            text_vectors[chapter] = self.get_vector_by_BOW(bag_of_n_grams, text, corpus)
        result = {}
        for chapter in text_vectors.keys():
            text_vector = text_vectors[chapter]
            result[chapter] = self.cosine_similarity(goal_vector, text_vector)
        max_result = max(result.values())
        for key, value in result.items():
            result[key] = value / max_result
        return result