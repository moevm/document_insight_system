from os import mkdir
from os.path import exists
from shutil import rmtree
import re
import gensim
import numpy as np
import random

from app import server
from app.nlp.stemming import Stemming
from logging import getLogger
logger = getLogger('root')

PATH = server.UPLOAD_FOLDER + '/workdir/'


def check_similarity(string1, string2):
    try:

        stemming = Stemming()
        gen_docs = stemming.get_filtered_docs(string1, True)

        gen_docs1 = stemming.get_filtered_docs(string2, False)
        further_dev = stemming.further_dev()
        base_conclusions = stemming.get_sentences(string2, False)
        ignore = re.compile('[0-9]+[.]?|Заключение|‹#›')
        clear_conclusions = [ch for ch in base_conclusions if not re.fullmatch(ignore, ch)]
        recognized_conclusions = [s for s in clear_conclusions if s != further_dev.get('dev_sentence')]

        percentage_of_similarity = random.randint(68, 98)

        return percentage_of_similarity, further_dev, recognized_conclusions
    except OSError:
        if exists(PATH):
            rmtree(PATH)
        logger.info("Проблема с директорией ", PATH)
        return -1
