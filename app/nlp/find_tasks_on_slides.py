from app.nlp.stemming import Stemming
from logging import getLogger
import itertools
from scipy.spatial import distance
logger = getLogger('root')

Task = 'Задачи:'


def compare_task_and_title(task, title):
    stemming = Stemming()
    parse_task = stemming.get_filtered_docs(task, False)
    parse_title = stemming.get_filtered_docs(title, False)

    task_set = set(list(itertools.chain(*parse_task)))
    title_set = set(list(itertools.chain(*parse_title)))

    l1 = []
    l2 = []
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

    cosine_similarity = ((1 - distance.cosine(l1, l2)) + 1)/2 #normalize
    return cosine_similarity


def find_tasks_on_slides(slide_goal_and_tasks, titles, intersection):
    try:
        stemming = Stemming()
        tasks = stemming.get_sentences(slide_goal_and_tasks, True)
        if len(tasks) == 0:
            return 'Задач не существует'

        cleaned_tasks = []
        found_descriptions = []
        task_count = 0
        slides_with_task = 0
        for task in tasks:
            if task == Task or task.isdigit():
                continue
            task_count += 1
            cleaned_tasks.append(task)
            for title in titles:
                if title == '':
                    continue
                similarity = compare_task_and_title(task, title) * 100
                if similarity >= intersection:
                    slides_with_task += 1
                    found_descriptions.append(task)
                    logger.info('\t\tВ презентации найдено описание задачи: ' + str(task))
                    break
        if task_count == slides_with_task:
            return 0
        return slides_with_task, list(set(cleaned_tasks) - set(found_descriptions))
    except Exception as error:
        return error
