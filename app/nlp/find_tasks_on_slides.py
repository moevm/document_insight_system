from app.nlp.stemming import Stemming
import re
import logging
logger = logging.getLogger('root_logger')
import itertools
from scipy.spatial import distance

def compare_task_and_title(task, title):
    #weak check, def doesn't work: CountVect/Tf-IdfVect
    stemming = Stemming()
    parse_task = stemming.get_filtered_docs(task, False)
    parse_title = stemming.get_filtered_docs(title, False)

    task_set = set(list(itertools.chain(*parse_task)))
    title_set = set(list(itertools.chain(*parse_title)))

    l1, l2 = [], []
    rvector = task_set.union(title_set)
    for w in rvector:
        if w in task_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in title_set:
            l2.append(1)
        else:
            l2.append(0)

    cosine_similarity = 1 - distance.cosine(l1, l2)
    return cosine_similarity


def find_tasks_on_slides(slide_goal_and_tasks, titles, intersection):
    try:
        stemming = Stemming()
        tasks = stemming.get_sentences(slide_goal_and_tasks, True)
        ignore = re.compile('[0-9][.]?|Задачи:|‹#›')  #[:]?
        cleaned_tasks = [task for task in tasks if not re.fullmatch(ignore, task)]
        logger=logging.getLogger('root_logger')
        logger.debug(str(slide_goal_and_tasks))
        logger.debug(str(tasks))
        logger.debug(str(ignore))
        logger.debug(str(cleaned_tasks))
        if len(cleaned_tasks) == 0:
            return 'Задач не существует'

        task_count = len(cleaned_tasks)
        found_descriptions = []
        cleaned_titles = list(filter(None, titles))
        for task in cleaned_tasks:
            for title in cleaned_titles:
                similarity = compare_task_and_title(task, title) * 100
                if similarity >= intersection:
                    found_descriptions.append(task)
                    break
        if task_count == len(found_descriptions):
            return 0
        return {'count': task_count,
                'recognized': cleaned_tasks,
                'not_found': list(set(cleaned_tasks) - set(found_descriptions))}
    except Exception as error:
        logger.error(error, exc_info=True)
        return str(error)
