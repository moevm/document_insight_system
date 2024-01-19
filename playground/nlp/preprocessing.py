import nltk
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.util import ngrams
import string


class NLPPreprocessor:
    def __init__(self, language='russian'):
        nltk.download('punkt')
        self.stemmer = SnowballStemmer(language)

    def preprocessing(self, text):
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def stemming(self, text):
        tokens = word_tokenize(text)
        stemmed_words = [self.stemmer.stem(word) for word in tokens]
        return stemmed_words

    def get_ngrams(self, tokens, n=2):
        result = []
        for i in range(n):
            n_grams = ngrams(tokens, i+1)
            result.extend([' '.join(grams) for grams in n_grams])
        return result

    def tokenization(self, stemmed_words):
        token_count = {}
        for word in stemmed_words:
            if word in token_count:
                token_count[word] += 1
            else:
                token_count[word] = 1
        return token_count

