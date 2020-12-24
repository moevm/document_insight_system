from app.nlp.stemming import Stemming

Task = 'Задачи:'


def compare_task_and_title(task, title):
    stemming = Stemming()
    parse_task = stemming.get_filtered_docs(task, False)
    parse_title = stemming.get_filtered_docs(title, False)
    task_set = set()
    title_set = set()
    for sent in parse_task:
        for word in sent:
            task_set.add(word)
    for sent in parse_title:
        for word in sent:
            title_set.add(word)
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
    c = 0

    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine


def find_tasks_on_slides(slide_goal_and_tasks, titles, intersection):
    try:
        stemming = Stemming()
        tasks = stemming.get_sentences(slide_goal_and_tasks, True)
        if len(tasks) == 0:
            return -1

        task_count = 0
        slides_with_task = 0
        for task in tasks:
            if task == Task or task.isdigit():
                continue
            task_count += 1
            for title in titles:
                if title == '':
                    continue
                similarity = compare_task_and_title(task, title) * 100
                if similarity >= intersection:
                    slides_with_task += 1
                    print('\t\tВ презентации найдено описание задачи: ' + str(task))
                    break
        if task_count == slides_with_task:
            return 0
        return -1
    except:
        return -1
