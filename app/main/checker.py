import re
import itertools
from argparse import Namespace
from flask_login import current_user
from app.nlp.find_tasks_on_slides import find_tasks_on_slides
from app.main.checks import SldNumCheck, SearchKeyWord, FindTasks, FindDefSld, \
                            SldEnumCheck, SldSimilarity, TitleFormatCheck, FurtherDev

from logging import getLogger
logger = getLogger('root')

key_slides = {'goals_and_tasks': 'Цель и задачи', 'approbation': 'Апробация', \
              'conclusion': 'Заключение', 'relevance': 'Актуальность'}
key_slide = Namespace(**key_slides)

def check(presentation, checks, presentation_name, username):

    if checks.slides_enum != -1:  # Нумерация слайдов
        checks.slides_enum = SldEnumCheck(presentation).check()
    if checks.slides_headers != -1:  # Заголовки слайдов занимают не более двух строк и существуют
        checks.slides_headers = TitleFormatCheck(presentation).check()

    if checks.goals_slide != -1:  # Слайд "Цель и задачи"
        checks.goals_slide = FindDefSld(presentation, key_slide.goals_and_tasks).check()
    if checks.probe_slide != -1:  # Слайд "Апробация работы"
        checks.probe_slide = FindDefSld(presentation, key_slide.approbation).check()
    if checks.actual_slide != -1:  # Слайд с описанием актуальности работы
        checks.actual_slide = SearchKeyWord(presentation, key_slide.relevance).check()
    if checks.conclusion_slide != -1:  # Слайд с заключением
        checks.conclusion_slide = FindDefSld(presentation, key_slide.conclusion).check()

    if checks.slides_number != -1:  # Количество основных слайдов
        checks.slides_number = SldNumCheck(presentation, checks.slides_number).check()
    if checks.conclusion_actual != -1:  # Соответствие заключения задачам
        checks.conclusion_actual =  SldSimilarity(presentation, key_slide.goals_and_tasks, key_slide.conclusion, checks.conclusion_actual).check()
    if checks.conclusion_along != -1:  # Наличие направлений дальнейшего развития
        checks.conclusion_along = FurtherDev(presentation, key_slide.goals_and_tasks, key_slide.conclusion).check()
    if checks.slide_every_task != -1:  # Наличие слайдов соответстующих задачам
        checks.slide_every_task = FindTasks(presentation, key_slide.goals_and_tasks, checks.slide_every_task).check()


    checks.score = checks.calc_score()
    checks.filename = presentation_name
    checks.user = username
    if current_user.params_for_passback:
        checks.is_passbacked = False

    return checks
