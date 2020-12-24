from re import split
from app.nlp.similarity_of_texts import check_similarity
from app.nlp.find_tasks_on_slides import find_tasks_on_slides


def __answer(mod, value):
    return {
        "pass": bool(mod),
        "value": str(value)
    }


def __check_slides_number(presentation, number, conclusion_slide_number):
    if conclusion_slide_number == -1 or conclusion_slide_number['value'] == '':
        conclusion_slide_number = len(presentation.slides)
    else:
        conclusion_slide_number = int(conclusion_slide_number['value'])
    print("\tКоличество основных слайдов в презентации равно " + str(conclusion_slide_number))
    return __answer(int(number) >= conclusion_slide_number, conclusion_slide_number)


def __check_slides_enumeration(presentation):
    error = ""
    if presentation.slides[0].page_number[0] != -1:
        error += "0 "
    for i in range(1, len(presentation.slides)):
        if presentation.slides[i].page_number[0] != i + 1:
            error += str(i) + " "
    print(("\tПлохо пронумерованные слайды: " + str(error)) if error != "" else "\tВсе слайды пронумерованы корректно")
    return __answer(error == "", error)


def __check_title_size(presentation):
    i = 0
    error_slides = ''
    for title in presentation.get_titles():
        i += 1
        if title == "":
            error_slides += str(i) + ' '
            continue

        title = str(title).replace('\x0b', '\n')
        if '\n' in title or '\r' in title:
            titles = []
            for t in split('\r|\n', title):
                if t != '':
                    titles.append(t)
            if len(titles) > 2:
                error_slides += str(i) + ' '
    print(("\tПлохо озаглавленные слайды: " + str(error_slides)) if error_slides != ""
          else "\tВсе слайды озаглавлены корректно")
    return __answer(error_slides == "", error_slides)


SLIDE_GOALS_AND_TASKS = 'Цель и задачи'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_CONCLUSION = 'Заключение'
SLIDE_WITH_RELEVANCE = 'Актуальность'


def __find_definite_slide(presentation, type_of_slide):
    i = 0
    for title in presentation.get_titles():
        i += 1
        if str(title).lower().find(str(type_of_slide).lower()) != -1:
            print("\tСлайд " + type_of_slide + " найден")
            return __answer(True, i), presentation.get_text_from_slides()[i - 1]
    print("\tСлайд " + type_of_slide + " не найден")
    return __answer(False, ""), ""


def __check_actual_slide(presentation):
    i = 0
    size = presentation.get_len_slides()
    for text in presentation.get_text_from_slides():
        i += 1
        if i > size:
            break
        if SLIDE_WITH_RELEVANCE.lower() in str(text).lower():
            print("\tСлайд " + SLIDE_WITH_RELEVANCE + " найден")
            return __answer(True, i)
    print("\tСлайд " + SLIDE_WITH_RELEVANCE + " не найден")
    return __answer(False, "")


def __are_slides_similar(goals, conclusions, number):
    if goals == "" or conclusions == "":
        return -1
    results = check_similarity(goals, conclusions)
    result = results[0]
    print('Result:' + str(result))
    print('Is further development on slide conclusion: ' + str(results[1]))
    return __answer(result >= number, result)


def __find_tasks_on_slides(presentation, goals_array):
    titles = presentation.get_titles()
    slides_with_tasks = find_tasks_on_slides(goals_array, titles)


def check(presentation, checks):
    goals_array = ""
    conclusion_array = ""

    if checks.slides_enum != -1:  # Нумерация слайдов
        checks.slides_enum = __check_slides_enumeration(presentation)
    if checks.slides_headers != -1:  # Заголовки слайдов занимают не более двух строк или заголовков нет
        checks.slides_headers = __check_title_size(presentation)

    if checks.goals_slide != -1:  # Слайд "Цель и задачи"
        checks.goals_slide, goals_array = __find_definite_slide(presentation, SLIDE_GOALS_AND_TASKS)
    if checks.probe_slide != -1:  # Слайд "Апробация работы"
        checks.probe_slide, aprobation_array = __find_definite_slide(presentation, SLIDE_APPROBATION_OF_WORK)
    if checks.actual_slide != -1:  # Слайд с описанием актуальности работы
        checks.actual_slide = __check_actual_slide(presentation)
    if checks.conclusion_slide != -1:  # Слайд с заключением
        checks.conclusion_slide, conclusion_array = __find_definite_slide(presentation, SLIDE_CONCLUSION)

    if checks.slides_number != -1:  # Количество основных слайдов
        checks.slides_number = __check_slides_number(presentation, checks.slides_number, checks.conclusion_slide)

    if checks.conclusion_actual != -1:  # Соответствие закличения задачам
        checks.conclusion_actual = __are_slides_similar(goals_array, conclusion_array, checks.conclusion_actual)
        __find_tasks_on_slides(presentation, goals_array)  # Наличие слайдов соответстующих задачам
    
    return checks
