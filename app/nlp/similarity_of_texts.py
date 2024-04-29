import re

from nlp.find_tasks_on_slides import compare_sentences
from nlp.stemming import Stemming


def check_similarity(string1, string2):
    stemming = Stemming()
    
    stemming.parse_text(string2, False)
    further_dev = stemming.further_dev()
    base_conclusions = stemming.sentences
    ignore = re.compile('[0-9]+[.]?|Заключение|‹#›')
    conclusions = [ch for ch in base_conclusions if not re.fullmatch(ignore, ch)]
    cleaned_conclusions = "\n".join(s for s in conclusions if s != further_dev.get('dev_sentence'))
    
    tasks = stemming.get_sentences(string1, True)
    ignore = re.compile('[0-9][.]?|Задачи:|‹#›')  # [:]?
    cleaned_tasks = "\n".join(task for task in tasks if not re.fullmatch(ignore, task))

    percentage_of_similarity = int(compare_sentences(cleaned_tasks, cleaned_conclusions) * 100)

    return percentage_of_similarity, further_dev, conclusions
