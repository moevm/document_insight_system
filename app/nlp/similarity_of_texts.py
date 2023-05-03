import re

from nlp.find_tasks_on_slides import compare_sentences
from nlp.stemming import Stemming


def check_similarity(string1, string2):
    stemming = Stemming()
    further_dev = stemming.further_dev()
    base_conclusions = stemming.get_sentences(string2, False)
    ignore = re.compile('[0-9]+[.]?|Заключение|‹#›')
    clear_conclusions = [ch for ch in base_conclusions if not re.fullmatch(ignore, ch)]
    recognized_conclusions = [s for s in clear_conclusions if s != further_dev.get('dev_sentence')]

    percentage_of_similarity = int(compare_sentences(string1, string2) * 100)

    return percentage_of_similarity, further_dev, recognized_conclusions
