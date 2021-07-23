import re
import itertools
from app.nlp.similarity_of_texts import check_similarity
from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from logging import getLogger
logger = getLogger('root')

def __answer(mod, value):
    return {
        "pass": bool(mod),
        "value": str(value)
    }

def get_sldnum_range(find_additional, slides_number, suspected_additional = None):
    if slides_number[0] <= find_additional <= slides_number[1]:
        return {'pass': True, 'value': find_additional,
                'verdict': 'Количество слайдов в допустимых границах'}
    elif find_additional <= slides_number[0]:
        return {'pass': False, 'value': find_additional,
                'verdict': 'Число слайдов меньше допустимого. Допустимые границы: {}'.format(slides_number)}
    else:
        if suspected_additional:
            return {'pass': False, 'value': find_additional,
                    'verdict': 'Допустимые границы: {}. Проверьте неозаглавленные запасные слайды'.format(slides_number)}
        else:
            return {'pass': False, 'value': find_additional,
                    'verdict': 'Число слайдов превышает допустимое. Допустимые границы: {}'.format(slides_number)}

def get_len_on_additional(presentation, slides_number):
    additional = re.compile('[А-Я][а-я]*[\s]слайд[ы]?')
    find_additional = [i for i, header in enumerate(presentation.get_titles()) if re.fullmatch(additional, header)]
    if len(find_additional) == 0:
        return get_sldnum_range(len(presentation.slides), slides_number, suspected_additional = True)
    else:
        return get_sldnum_range(find_additional[0], slides_number)

def __check_slides_enumeration(presentation):
    error = []
    if presentation.slides[0].page_number[0] != -1:
        error.append(1)
    for i in range(1, len(presentation.slides)):
        if presentation.slides[i].page_number[0] != i + 1:
            error.append(i+1)
    logger.info(("\tПлохо пронумерованные слайды: " + str(error)) if error != [] else "\tВсе слайды пронумерованы корректно")
    return {'pass': error == [], 'value': error}


def __check_title_size(presentation):
    i = 0
    empty_headers = []
    len_exceeded = []
    for title in presentation.get_titles():
        i += 1
        if title == "":
            empty_headers.append(i)
            continue

        title = str(title).replace('\x0b', '\n')
        if '\n' in title or '\r' in title:
            titles = []
            for t in re.split('\r|\n', title):
                if t != '':
                    titles.append(t)
            if len(titles) > 2:
                len_exceeded.append(i)
    error_slides = list(itertools.chain(empty_headers, len_exceeded))
    logger.info(("\tПлохо озаглавленные слайды: " + str(error_slides)) if error_slides != []
          else "\tВсе слайды озаглавлены корректно")
    if not error_slides:
        return {'pass': not bool(error_slides) , 'value': [empty_headers, len_exceeded],
                'verdict': ["Пройдена!"]}
    elif len(empty_headers) == 0 and len(len_exceeded) != 0:
        return {'pass': False, 'value': len_exceeded,
                'verdict': ['Превышение длины: {}'.format(', '.join(map(str, len_exceeded))),
                            'Убедитесь в корректности заголовка и текста слайда']}
    elif len(empty_headers) != 0 and len(len_exceeded) == 0:
        return {'pass':False, 'value': empty_headers,
                'verdict': ['Заголовки не найдены: {}.'.format(', '.join(map(str, empty_headers))),
                            'Убедитесь, что слайд озаглавлен соответстующим элементом']}
    else:
        return {'pass':False, 'value': [empty_headers, len_exceeded],
                'verdict': ['Заголовки не найдены: {}.'.format(', '.join(map(str, empty_headers))),
                'Убедитесь, что слайд озаглавлен соответстующим элементом',
                'Превышение длины: {}'.format(', '.join(map(str, len_exceeded))),
                 'Убедитесь в корректности заголовка и текста слайда']}

SLIDE_GOALS_AND_TASKS = 'Цель и задачи'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_CONCLUSION = 'Заключение'
SLIDE_WITH_RELEVANCE = 'Актуальность'


def __find_definite_slide(presentation, type_of_slide):
    i = 0
    found_slides = []
    found_idxs = []
    for title in presentation.get_titles():
        i += 1
        if str(title).lower().find(str(type_of_slide).lower()) != -1:
            logger.info("\tСлайд " + type_of_slide + " найден")
            found_slides.append(presentation.get_text_from_slides()[i - 1])
            found_idxs.append(i)
    if len(found_slides) == 0:
        logger.info("\tСлайд " + type_of_slide + " не найден")
        return __answer(False, ""), ""
    else:
        return {'pass': True, 'value': found_idxs}, ' '.join(found_slides)


def __check_actual_slide(presentation):
    i = 0
    size = presentation.get_len_slides()
    for text in presentation.get_text_from_slides():
        i += 1
        if i > size:
            break
        if SLIDE_WITH_RELEVANCE.lower() in str(text).lower():
            logger.info("\tСлайд " + SLIDE_WITH_RELEVANCE + " найден")
            return __answer(True, i)
    logger.info("\tСлайд " + SLIDE_WITH_RELEVANCE + " не найден")
    return __answer(False, "")


def __are_slides_similar(goals, conclusions, actual_number):
    if goals == "" or conclusions == "":
        return -1

    results = check_similarity(goals, conclusions)
    if results == -1:
        return __answer(False, "Произошла ошибка!"), __answer(False, "Произошла ошибка!")
    else:
        return __answer(results[0] >= actual_number, results[0]),    \
               {'pass': results[1].get('found_dev'), 'value': results[1].get('dev_sentence')}


def __find_tasks_on_slides(presentation, goals, intersection_number):
    if goals == "":
        return __answer(False, 'Слайд "Задачи" не найден')

    titles = presentation.get_titles()
    slides_with_tasks = find_tasks_on_slides(goals, titles, intersection_number)

    if slides_with_tasks == 0:
        logger.info("\tВсе заявленные задачи найдены на слайдах")
        return __answer(True, "Все задачи найдены на слайдах")
    else:
        logger.info("\tНекоторые из заявленных задач на слайдах не найдены")
        return {'pass': False, 'value': slides_with_tasks}


def check(presentation, checks, presentation_name, username):
    goals_array = ""
    conclusion_array = ""

    if checks.slides_enum != -1:  # Нумерация слайдов
        checks.slides_enum = __check_slides_enumeration(presentation)
    if checks.slides_headers != -1:  # Заголовки слайдов занимают не более двух строк и существуют
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
        checks.slides_number = get_len_on_additional(presentation, checks.slides_number)

    similar = __are_slides_similar(goals_array, conclusion_array, checks.conclusion_actual)
    if checks.conclusion_actual != -1:  # Соответствие заключения задачам
        if similar != -1:
            logger.info("\tОбозначенные цели совпадают с задачами на " + similar[0]['value'] + "%")
            checks.conclusion_actual = similar[0]
        else:
            checks.conclusion_actual = {'pass': False, 'value': 0}
    if checks.conclusion_along != -1:  # Наличие направлений дальнейшего развития
        if similar != -1:
            logger.info("\tНаправления дальнейшего развития " + ("" if similar[1]['value'] else "не ") + "найдены")
            checks.conclusion_along = similar[1]
        else:
            checks.conclusion_along = {'pass': False}

    if checks.slide_every_task != -1:  # Наличие слайдов соответстующих задачам
        checks.slide_every_task = __find_tasks_on_slides(presentation, goals_array, checks.slide_every_task)


    checks.score = checks.calc_score()
    checks.filename = presentation_name
    checks.user = username

    return checks
