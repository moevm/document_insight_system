from os import remove
from os.path import exists
from re import split

from app.nlp.similarity_of_texts import check_similarity


def __check_slides_number(presentation):
    return -1


def __check_slides_enumeration(presentation):
    error = ""
    if presentation.slides[0].page_number[0] != -1:
        error += "0 "
    for i in range(1, len(presentation.slides)):
        if presentation.slides[i].page_number[0] != i + 1:
            error += str(i) + " "
    return error


def __check_title_size(presentation):
    i = 0
    error_slides = ''
    for title in presentation.get_titles():
        i += 1
        title = str(title).replace('\x0b', '\n')
        if '\n' in title or '\r' in title:
            titles = []
            for t in split('\r|\n', title):
                if t != '':
                    titles.append(t)
            if len(titles) > 2:
                error_slides += str(i) + ' '
    return error_slides


SLIDE_GOALS_AND_TASKS = 'Цель и задачи'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_CONCLUSION = 'Заключение'


def __find_definite_slide(presentation, type_of_slide):
    i = 0
    for title in presentation.get_titles():
        i += 1
        if str(title).lower().find(str(type_of_slide).lower()) != -1:
            return str(i), presentation.get_text_from_slides()[i - 1]
    return "", ""


def __check_actual_slide(presentation):
    return -1


def __are_slides_similar(goals, conclusions):
    if goals == "" or conclusions == "":
        return -1
    result = check_similarity(goals, conclusions)
    print('Result:' + str(result))
    return result


def check(presentation, checks):
    goals_array = ""
    aprobation_array = ""
    conclusion_array = ""

    if checks.slides_number != -1:  # Количество основных слайдов
        checks.slides_number = __check_slides_number(presentation)
    if checks.slides_enum != -1:  # Нумерация слайдов
        checks.slides_enum = __check_slides_enumeration(presentation)
    if checks.slides_headers != -1:  # Заголовки слайдов занимают не более двух строк
        checks.slides_headers = __check_title_size(presentation)
    if checks.goals_slide != -1:  # Слайд "Цель и задачи"
        checks.goals_slide, goals_array = __find_definite_slide(presentation, SLIDE_GOALS_AND_TASKS)
    if checks.probe_slide != -1:  # Слайд "Апробация работы"
        checks.probe_slide, aprobation_array = __find_definite_slide(presentation, SLIDE_APPROBATION_OF_WORK)
    if checks.actual_slide != -1:  # Слайд с описанием актуальности работы
        checks.actual_slide = __check_actual_slide(presentation)
    if checks.conclusion_slide != -1:  # Слайд с заключением
        checks.conclusion_slide, conclusion_array = __find_definite_slide(presentation, SLIDE_CONCLUSION)
    if checks.conclusion_actual != -1:  # Соответствие закличения задачам
        checks.conclusion_actual = __are_slides_similar(goals_array, conclusion_array)

    return checks
