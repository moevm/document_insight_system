from argparse import Namespace
from app.main.checks import (FindDefSld, FindTasks, FurtherDev, SearchKeyWord,
                             SldEnumCheck, SldNumCheck, SldSimilarity,
                             TemplateNameCheck, TitleFormatCheck)

key_slides = {
              'goals_and_tasks': 'Цель и задачи',
              'approbation': 'Апробация',
              'conclusion': 'Заключение',
              'relevance': ['Актуальность', 'Актуальности', 'Актуальностью']
              }
key_slide = Namespace(**key_slides)

def check(presentation, checks, presentation_name):
    check_names = checks.enabled_checks.keys()
    set_enabled = dict.fromkeys(check_names, False)
    set_checks = {
        'template_name': TemplateNameCheck(presentation, presentation_name),
        'slides_number': SldNumCheck(presentation, checks.enabled_checks['slides_number']),
        'slides_enum': SldEnumCheck(presentation, checks.conv_pdf_fs_id),
        'slides_headers': TitleFormatCheck(presentation, checks.conv_pdf_fs_id),
        'goals_slide': FindDefSld(presentation, key_slide.goals_and_tasks, checks.conv_pdf_fs_id),
        'probe_slide': FindDefSld(presentation, key_slide.approbation, checks.conv_pdf_fs_id),
        'actual_slide': SearchKeyWord(presentation, key_slide.relevance, checks.conv_pdf_fs_id),
        'conclusion_slide': FindDefSld(presentation, key_slide.conclusion, checks.conv_pdf_fs_id),
        'slide_every_task': FindTasks(presentation, key_slide.goals_and_tasks, checks.enabled_checks['slide_every_task']),
        'conclusion_actual': SldSimilarity(presentation, key_slide.goals_and_tasks, key_slide.conclusion, checks.enabled_checks['conclusion_actual']),
        'conclusion_along': FurtherDev(presentation, key_slide.goals_and_tasks, key_slide.conclusion, checks.conv_pdf_fs_id)
    }
    enabled_checks = dict((key, value) for key, value in checks.enabled_checks.items() if value)

    for k, v in enabled_checks.items():
        set_enabled[k] = set_checks[k].check()

    checks.enabled_checks = set_enabled
    checks.score = checks.calc_score()
    checks.filename = presentation_name

    return checks
