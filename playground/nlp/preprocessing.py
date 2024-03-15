from collections import Counter, defaultdict

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
            n_grams = ngrams(tokens, i+1)
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

    def get_vector_by_BOW(self, bag_of_ngramms, doc):
        count_dict = defaultdict(int)
        vec = np.zeros(len(bag_of_ngramms))
        for item in doc:
            count_dict[item] += 1
        for key, item in count_dict.items():
            vec[bag_of_ngramms[key]] = item
        return vec

    def cosine_similarity(self, vector1, vector2):
            text1_norm = float(len(vector1)) ** 0.5
            text2_norm = float(len(vector2)) ** 0.5
            dot_product = sum(gram_a * gram_b for gram_a, gram_b in zip(vector1, vector2))
            cosine_sim = dot_product / (text1_norm * text2_norm)

            return cosine_sim


# Пример использования
nlp_processor = NLPProcessor()

text1 = "Реализация алгоритма поиска и отслеживания точек интереса для измерения пульса по видео"
text2 = "Проанализировать существующие решения для определения видимых областей лица человека и для определения перекрытий объектов, На основе анализа существующих решений сформулировать требования к реализации алгоритма, Реализовать алгоритм поиска и отслеживания точек интереса, Исследовать свойства реализованного алгоритма"

tokens1 = nlp_processor.preprocessing(text1)
n_grams1 = nlp_processor.get_ngrams(tokens1)

tokens2 = nlp_processor.preprocessing(text2)
n_grams2 = nlp_processor.get_ngrams(tokens2)

docs = [n_grams1, n_grams2]
bag_of_ngrams = nlp_processor.get_bag_of_n_gramms(docs)
vector1 = nlp_processor.get_vector_by_BOW(bag_of_ngrams, n_grams1)
vector2 = nlp_processor.get_vector_by_BOW(bag_of_ngrams, n_grams2)
print(f"Согласно косиносному сходству, веторы похожи на {nlp_processor.cosine_similarity(vector1, vector2)}")