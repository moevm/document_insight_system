import nltk
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
        return tokens

    def stemming(self, tokens):
        stemmed_words = [self.stemmer.stem(word) for word in tokens]
        return stemmed_words

    def get_ngrams(self, tokens, n=2):
        result = []
        for i in range(n):
            n_grams = ngrams(tokens, i+1)
            result.extend([' '.join(grams) for grams in n_grams])
        return result


# # Пример использования
# nlp_processor = NLPProcessor()
#
# text = "Пример текста для стемминга и токенизации. Текст содержит повторяющиеся слова для создания n-грамм."
# tokens = nlp_processor.preprocessing(text)
# stemmed_words = nlp_processor.stemming(tokens)
# n_grams = nlp_processor.get_ngrams(stemmed_words)
#
# print("Текст:", text)
# print("Стеммированные слова:", stemmed_words)
# print("N-граммы:", n_grams)
# print("Матрица n-грамм:")
