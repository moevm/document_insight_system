from TextPreprocessing import TextProcessing
from compareTexts import compareTexts
import codecs
import os

PATH_TO_TEXTS = "../texts"

if __name__ == "__main__":
    _, _, files = next(os.walk(PATH_TO_TEXTS))
    for i in range(len(files)):
        check_text = codecs.open(PATH_TO_TEXTS + "/" + files[i], encoding='utf-8')
        Text1 = TextProcessing(check_text.read()).processText()
        for j in range(len(files)):
            if files[i] == files[j]:
                continue
            suspect_text = codecs.open(PATH_TO_TEXTS + "/" + files[j], encoding='utf-8')
            Text2 = TextProcessing(suspect_text.read()).processText()
            percent = compareTexts(Text1, Text2)
            print('{}% of the {} is borrowed from {}'.format(percent, files[i], files[j]))
        print("---------------------------------------------")
        print()
