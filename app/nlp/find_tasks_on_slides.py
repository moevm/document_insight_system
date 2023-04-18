import logging
import re

from nlp.stemming import Stemming
from scipy.spatial import distance

logger = logging.getLogger('root_logger')


def compare_sentences(sentence_1, sentence_2):
    # weak check, def doesn't work: CountVect/Tf-IdfVect
    stemming = Stemming()
    set_1 = stemming.get_filtered_docs(sentence_1, False)
    set_2 = stemming.get_filtered_docs(sentence_2, False)
    rvector = set_1.union(set_2)
    vector_1 = [w in set_1 for w in rvector]
    vector_2 = [w in set_2 for w in rvector]
    cosine_similarity = 1 - distance.cosine(vector_1, vector_2)
    return cosine_similarity


def find_tasks_on_slides(slide_goal_and_tasks, titles, intersection):
    try:
        stemming = Stemming()
        tasks = stemming.get_sentences(slide_goal_and_tasks, True)
        ignore = re.compile('[0-9][.]?|Задачи:|‹#›')  # [:]?
        cleaned_tasks = [task for task in tasks if not re.fullmatch(ignore, task)]
        task_count = len(cleaned_tasks)
        logger.debug(str({
            'slide_goal_and_tasks': slide_goal_and_tasks,
            'tasks': tasks,
            'cleaned_tasks': cleaned_tasks
        }))
        if len(cleaned_tasks) == 0:
            return 'Задач не существует'

        found_descriptions = []
        cleaned_titles = set(filter(None, titles))
        for task in cleaned_tasks:
            founded_title = None
            for title in cleaned_titles:
                similarity = compare_sentences(task, title) * 100
                if similarity >= intersection:
                    found_descriptions.append(task)
                    founded_title = title
                    break
            cleaned_titles.discard(founded_title)  # remove founded title
        not_found_tasks = list(set(cleaned_tasks) - set(found_descriptions))
        return {
            'count': task_count,
            'recognized': cleaned_tasks,
            'not_found': not_found_tasks,
            'found_ratio': (task_count - len(not_found_tasks)) / task_count
        }
    except Exception as error:
        logger.error(error, exc_info=True)
        return str(error)
