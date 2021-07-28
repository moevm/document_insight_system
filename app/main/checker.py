import re
import itertools
from app.nlp.similarity_of_texts import check_similarity
from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from app.main.checker_util import SldNumCheck, answer
from logging import getLogger
logger = getLogger('root')

def __check_slides_enumeration(presentation):
    error = []
    if presentation.slides[0].page_number[0] != -1:
        error.append(1)
    for i in range(1, len(presentation.slides)):
        if presentation.slides[i].page_number[0] != i + 1:
            error.append(i+1)
    logger.info(("\tПлохо пронумерованные слайды: " + str(error)) if error else "\tВсе слайды пронумерованы корректно")
    if not error:
        return answer(True, error, ["Пройдена!"])
    else:
        return answer(False, error, ['Не пройдена, проблемные слайды: {}'.format(', '.join(map(str, error))),
                                     'Убедитесь в корректности формата номеров слайдов'])

def __check_title_size(presentation):
    empty_headers, len_exceeded = [], []
    for i, title in enumerate(presentation.get_titles(), 1):
        if title == "":
            empty_headers.append(i)
            continue

        title = str(title).replace('\x0b', '\n')
        if '\n' in title or '\r' in title:
            titles = [t for t in re.split('\r|\n', title) if t != '']
            if len(titles) > 2:
                len_exceeded.append(i)
    error_slides = list(itertools.chain(empty_headers, len_exceeded))
    logger.info(("\tПлохо озаглавленные слайды: " + str(error_slides)) if error_slides
          else "\tВсе слайды озаглавлены корректно")

    def exceeded_verdict(len_exceeded):
        return ['Превышение длины: {}'.format(', '.join(map(str, len_exceeded))),
                'Убедитесь в корректности заголовка и текста слайда']

    def empty_verdict(empty_headers):
        return ['Заголовки не найдены: {}.'.format(', '.join(map(str, empty_headers))),
                'Убедитесь, что слайд озаглавлен соответстующим элементом']

    if not error_slides:
        return answer(not bool(error_slides), [empty_headers, len_exceeded], ["Пройдена!"])
    elif len(empty_headers) == 0 and len(len_exceeded) != 0:
        return answer(False, len_exceeded, exceeded_verdict(len_exceeded))
    elif len(empty_headers) != 0 and len(len_exceeded) == 0:
        return answer(False, empty_headers, empty_verdict(empty_headers))
    else:
        return answer(False, [empty_headers, len_exceeded],
               list(itertools.chain(empty_verdict(empty_headers), exceeded_verdict(len_exceeded))))

SLIDE_GOALS_AND_TASKS = 'Цель и задачи'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_CONCLUSION = 'Заключение'
SLIDE_WITH_RELEVANCE = 'Актуальность'


def __find_definite_slide(presentation, type_of_slide):
    found_slides, found_idxs  = [], []
    for i, title in enumerate(presentation.get_titles(), 1):
        if str(title).lower().find(str(type_of_slide).lower()) != -1:
            logger.info("\tСлайд " + type_of_slide + " найден")
            found_slides.append(presentation.get_text_from_slides()[i - 1])
            found_idxs.append(i)
    if len(found_slides) == 0:
        logger.info("\tСлайд " + type_of_slide + " не найден")
        return answer(False, None, ['Слайд не найден'])
    else:
        return answer(True, found_idxs, ['Слайд найден']), ' '.join(found_slides)


def __check_actual_slide(presentation):
    for i, text in enumerate(presentation.get_text_from_slides(), 1):
        if SLIDE_WITH_RELEVANCE.lower() in str(text).lower():
            logger.info("\tСлайд " + SLIDE_WITH_RELEVANCE + " найден")
            return answer(True, i, ['Найден под номером: {}'.format(i)])
    logger.info("\tСлайд " + SLIDE_WITH_RELEVANCE + " не найден")
    return answer(False, None, ['Слайд не найден'])


def __are_slides_similar(goals, conclusions, actual_number):
    if goals == "" or conclusions == "":
        return answer(False, None, ['Задач или заключения не существует'])

    results = check_similarity(goals, conclusions)
    if results == -1:
        return answer(False, None, ["Произошла ошибка!"]), answer(False, None, ["Произошла ошибка!"])
    else:
        return (answer(results[0] >= actual_number, results[0], ['Соответствует на {}%'.format(results[0])]),
                answer(results[1].get('found_dev'), results[1].get('dev_sentence'), [results[1].get('dev_sentence')]))


def __find_tasks_on_slides(presentation, goals, intersection_number):
    if goals == "":
        return answer(False, None, ['Слайд "Задачи" не найден'])

    titles = presentation.get_titles()
    slides_with_tasks = find_tasks_on_slides(goals, titles, intersection_number)

    if slides_with_tasks == 0:
        logger.info("\tВсе заявленные задачи найдены на слайдах")
        return {'pass': True, 'value': "Все задачи найдены на слайдах",
                'verdict': ["Все задачи найдены на слайдах"]}
    elif len(slides_with_tasks) == 2 :
        logger.info("\tНекоторые из заявленных задач на слайдах не найдены")
        swt_verdict = ['Всего задач: {}'.format(slides_with_tasks.get('count')),
                       'Не найдены: ']
        swt_verdict.extend(slides_with_tasks.get('not_found'))
        return answer(False, slides_with_tasks, swt_verdict)
    else:
        return answer(False, slides_with_tasks, slides_with_tasks)


def check(presentation, checks, presentation_name, username):
    goals_array, conclusion_array = "", ""

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
        checks.slides_number = SldNumCheck(presentation, checks.slides_number).get_len_on_additional()

    similar = __are_slides_similar(goals_array, conclusion_array, checks.conclusion_actual)
    if checks.conclusion_actual != -1:  # Соответствие заключения задачам
        if similar != -1:
            checks.conclusion_actual = similar[0]
        else:
            checks.conclusion_actual = {'pass': False, 'value': 0}
    if checks.conclusion_along != -1:  # Наличие направлений дальнейшего развития
        if similar != -1:
            checks.conclusion_along = similar[1]
        else:
            checks.conclusion_along = {'pass': False}

    if checks.slide_every_task != -1:  # Наличие слайдов соответстующих задачам
        checks.slide_every_task = __find_tasks_on_slides(presentation, goals_array, checks.slide_every_task)


    checks.score = checks.calc_score()
    checks.filename = presentation_name
    checks.user = username

    return checks
