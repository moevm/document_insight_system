import re
import itertools
from flask_login import current_user
from app.nlp.similarity_of_texts import check_similarity
from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from app.utils.parse_for_html import find_tasks_on_slides_feedback, tasks_conclusions_feedback
from app.main.checks.sld_num import SldNumCheck
from app.main.checks.title_format import TitleFormatCheck
from app.main.checks.base_check import answer
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
        return answer(True, error, "Пройдена!")
    else:
        return answer(False, error, 'Не пройдена, проблемные слайды: {}'.format(', '.join(map(str, error))), \
                                    'Убедитесь в корректности формата номеров слайдов')


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
        return answer(False, None, 'Слайд не найден'), ''
    else:
        return answer(True, found_idxs, 'Найден под номером: {}'.format(', '.join(map(str, found_idxs)))), ' '.join(found_slides)


def __check_actual_slide(presentation):
    for i, text in enumerate(presentation.get_text_from_slides(), 1):
        if SLIDE_WITH_RELEVANCE.lower() in str(text).lower():
            logger.info("\tСлайд " + SLIDE_WITH_RELEVANCE + " найден")
            return answer(True, i, 'Найден под номером: {}'.format(i))
    logger.info("\tСлайд " + SLIDE_WITH_RELEVANCE + " не найден")
    return answer(False, None, 'Слайд не найден')


def __are_slides_similar(goals, conclusions, actual_number):
    if goals == "" or conclusions == "":
        return answer(False, 0, 'Задач или заключения не существует'), answer(False, 0, 'Задач или заключения не существует')

    results = check_similarity(goals, conclusions)
    if results == -1:
        return answer(False, None, "Произошла ошибка!"), answer(False, None, "Произошла ошибка!")
    else:
        return (answer(results[0] >= actual_number, results[0], *tasks_conclusions_feedback(results)),
                answer(results[1].get('found_dev'), results[1].get('dev_sentence'), results[1].get('dev_sentence')))


def __find_tasks_on_slides(presentation, goals, intersection_number):
    if goals == "":
        return answer(False, None, 'Слайд "Задачи" не найден')

    titles = presentation.get_titles()
    slides_with_tasks = find_tasks_on_slides(goals, titles, intersection_number)

    if slides_with_tasks == 0:
        logger.info("\tВсе заявленные задачи найдены на слайдах")
        return answer(True, "Все задачи найдены на слайдах", "Все задачи найдены на слайдах")
    elif len(slides_with_tasks) == 3 :
        logger.info("\tНекоторые из заявленных задач на слайдах не найдены")
        return answer(False, slides_with_tasks, *find_tasks_on_slides_feedback(slides_with_tasks))
    elif len(slides_with_tasks) == 1:
        return answer(False, slides_with_tasks, slides_with_tasks)


def check(presentation, checks, presentation_name, username):
    goals_array, conclusion_array = "", ""

    if checks.slides_enum != -1:  # Нумерация слайдов
        checks.slides_enum = __check_slides_enumeration(presentation)
    if checks.slides_headers != -1:  # Заголовки слайдов занимают не более двух строк и существуют
        checks.slides_headers = TitleFormatCheck(presentation).check()

    if checks.goals_slide != -1:  # Слайд "Цель и задачи"
        checks.goals_slide, goals_array = __find_definite_slide(presentation, SLIDE_GOALS_AND_TASKS)
    if checks.probe_slide != -1:  # Слайд "Апробация работы"
        checks.probe_slide, aprobation_array = __find_definite_slide(presentation, SLIDE_APPROBATION_OF_WORK)
    if checks.actual_slide != -1:  # Слайд с описанием актуальности работы
        checks.actual_slide = __check_actual_slide(presentation)
    if checks.conclusion_slide != -1:  # Слайд с заключением
        checks.conclusion_slide, conclusion_array = __find_definite_slide(presentation, SLIDE_CONCLUSION)

    if checks.slides_number != -1:  # Количество основных слайдов
        checks.slides_number = SldNumCheck(presentation, checks.slides_number).check()

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
    if current_user.params_for_passback:
        checks.is_passbacked = False

    return checks
