import re
import pymorphy2
import nltk
from nltk.corpus import stopwords
import hashlib

nltk.download('stopwords')
morph = pymorphy2.MorphAnalyzer()


class TextProcessing:
    def __init__(self, text):
        if text == "" or type(text) is not str:
            raise Exception("Empty text or not string")

        EngToRuDict = {65: 1040, 66: 1042, 67: 1057, 69: 1045, 79: 1054, 80: 1056, 72: 1053, 84: 1058, 97: 1072,
                       99: 1089, 101: 1077, 111: 1086, 112: 1088, 120: 1093, 121: 1091}

        for i in range(len(text)):
            if str.isalpha(text[i]):
                if not 1040 <= ord(text[i]) <= 1103:
                    try:
                        text = text[:i] + chr(EngToRuDict[ord(text[i])]) + text[i + 1:]
                    except KeyError:
                        continue

        self._text = text
        self.processedText = None
        self.hashedText = []

    def deleteDigits(self):
        self._text = re.sub(r"\d-[а-я]*", ' ', self._text)
        self._text = re.sub(r"\d[а-я]*", ' ', self._text)
        self._text = re.sub(r"\d", ' ', self._text)

    def lemmatization(self):
        self.processedText = ' '.join(self.processedText)
        words = self.processedText.split()
        res = []
        for word in words:
            temp = morph.parse(word)[0]
            res.append(temp.normal_form)
        self.processedText = res

    def divideTextIntoShingles(self):
        shingleSize = 5
        shingles = [self.processedText[i:i + shingleSize] for i in range(len(self.processedText))][:-shingleSize]
        for shingle in shingles:
            hash_obj = hashlib.sha1(' '.join(shingle).encode()).hexdigest()
            self.hashedText.append(hash_obj)

    def processText(self):
        setOfStopWords = stopwords.words('russian')

        self._text = self._text.replace('\r', ' ')
        tempText = self._text.split(' ')

        for i in range(0, len(tempText)):
            if tempText[i].lower().replace('\r', '').replace('\n', '') in setOfStopWords:
                tempText[i] = ''
            else:
                tempText[i] = tempText[i].lower().replace('\n', '')

        self.processedText = []
        it = 0
        while it < len(tempText):
            if tempText[it] != '':
                self.processedText.append(tempText[it])
                del tempText[it]
            else:
                it += 1
        self.lemmatization()
        self.divideTextIntoShingles()
        return self.hashedText
