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

    def get_ngrams(self, tokens, n=1):
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
            return np.log10((len(docs) + 1) / (word_in_docs + 1))

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
        cosine_sim = dot_product / (norm1 * norm2)
        return cosine_sim

    def example(self, goal, text):
        corpus = []
        goal_n_grams = []
        for paragraph in goal:
            if paragraph:
                tokens1 = self.preprocessing(paragraph)
                n_grams1 = self.get_ngrams(tokens1)
                goal_n_grams.append(n_grams1)

        text_n_grams = []
        for paragraph in text:
            if paragraph:
                tokens2 = self.preprocessing(paragraph)
                n_grams2 = self.get_ngrams(tokens2)
                text_n_grams.append(n_grams2)

        corpus.extend(goal_n_grams)
        corpus.extend(text_n_grams)
        bag_of_n_grams = self.get_bag_of_n_gramms(corpus)
        goal_vector = self.get_vector_by_BOW(bag_of_n_grams, goal_n_grams[0], corpus)
        text_vectors = []
        for paragraph in text_n_grams:
            text_vectors.append(self.get_vector_by_BOW(bag_of_n_grams, paragraph, corpus))
        results = []
        for i, text_vector in enumerate(text_vectors):
            result = self.cosine_similarity(goal_vector, text_vector)
            results.append(result)
        for index, value in enumerate(results):
            print(f"Абзац {index + 1} схож с целью на {results[index]}")
        print(f"В среднем: {sum(results) / len(results)}")

        print('\n')


if __name__ == '__main__':
    nlp_processor = NLPProcessor()

    text1 = open("text_1").read().split('\n')
    text2 = open("text_2").read().split('\n')
    goal1 = open("goal_1").read().split('\n')
    goal2 = open("goal_2").read().split('\n')
    nlp_processor.example(goal1, text1)
    nlp_processor.example(goal1, text2)
    nlp_processor.example(goal2, text1)
    nlp_processor.example(goal2, text2)
