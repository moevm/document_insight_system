from argparse import Namespace
from flask_login import current_user
from app.main.checks import SldNumCheck, SearchKeyWord, FindTasks, FindDefSld, \
                            SldEnumCheck, SldSimilarity, TitleFormatCheck, FurtherDev

from logging import getLogger
logger = getLogger('root')

key_slides = {'goals_and_tasks': 'Цель и задачи', 'approbation': 'Апробация', \
              'conclusion': 'Заключение', 'relevance': 'Актуальность'}
key_slide = Namespace(**key_slides)

def check(presentation, checks, presentation_name):
    check_names = checks.get_checks().keys()
    check_classes = [SldNumCheck(presentation, checks.slides_number), SldEnumCheck(presentation, checks.conv_pdf_fs_id), TitleFormatCheck(presentation, checks.conv_pdf_fs_id), \
                     FindDefSld(presentation, key_slide.goals_and_tasks, checks.conv_pdf_fs_id), FindDefSld(presentation, key_slide.approbation, checks.conv_pdf_fs_id), \
                     SearchKeyWord(presentation, key_slide.relevance, checks.conv_pdf_fs_id), FindDefSld(presentation, key_slide.conclusion, checks.conv_pdf_fs_id), \
                     FindTasks(presentation, key_slide.goals_and_tasks, checks.slide_every_task), \
                     SldSimilarity(presentation, key_slide.goals_and_tasks, key_slide.conclusion, checks.conclusion_actual),
                     FurtherDev(presentation, key_slide.goals_and_tasks, key_slide.conclusion, checks.conv_pdf_fs_id)]
    set_checks = dict(zip(check_names, check_classes))
    enabled_checks = dict((key, value) for key, value in checks.get_checks().items() if value)
    for ch in enabled_checks:
        setattr(checks, ch, set_checks[ch].check())

    checks.score = checks.calc_score()
    checks.filename = presentation_name
    checks.user = current_user.username
    checks.lms_user_id = current_user.lms_user_id
    if current_user.params_for_passback:
        checks.is_passbacked = False

    return checks
