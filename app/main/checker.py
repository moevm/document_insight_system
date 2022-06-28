from argparse import Namespace

from .checks import ReportSimpleCheck, SldNumCheck, SearchKeyWord, FindTasks, FindDefSld, SldEnumCheck, SldSimilarity, \
    TitleFormatCheck, FurtherDev, TemplateNameCheck, ReportImageShareCheck

key_slides = {
    'goals_and_tasks': 'Цель и задачи',
    'approbation': 'Апробация',
    'conclusion': 'Заключение',
    'relevance': ['Актуальность', 'Актуальности', 'Актуальностью']
}
key_slide = Namespace(**key_slides)


def check(parsed_file, checks, filename, user):
    check_names = checks.enabled_checks.keys()
    set_enabled = dict.fromkeys(check_names, False)
    # TODO: create only enabled checks (because checks may not contain some info?)
    set_checks = {
        'template_name': TemplateNameCheck(parsed_file, filename),
        'slides_number': SldNumCheck(parsed_file, checks.enabled_checks['slides_number']),
        'slides_enum': SldEnumCheck(parsed_file, checks.conv_pdf_fs_id),
        'slides_headers': TitleFormatCheck(parsed_file, checks.conv_pdf_fs_id),
        'goals_slide': FindDefSld(parsed_file, key_slide.goals_and_tasks, checks.conv_pdf_fs_id),
        'probe_slide': FindDefSld(parsed_file, key_slide.approbation, checks.conv_pdf_fs_id),
        'actual_slide': SearchKeyWord(parsed_file, key_slide.relevance, checks.conv_pdf_fs_id),
        'conclusion_slide': FindDefSld(parsed_file, key_slide.conclusion, checks.conv_pdf_fs_id),
        'slide_every_task': FindTasks(parsed_file, key_slide.goals_and_tasks,
                                      checks.enabled_checks['slide_every_task']),
        'conclusion_actual': SldSimilarity(parsed_file, key_slide.goals_and_tasks, key_slide.conclusion,
                                           checks.enabled_checks['conclusion_actual']),
        'conclusion_along': FurtherDev(parsed_file, key_slide.goals_and_tasks, key_slide.conclusion,
                                       checks.conv_pdf_fs_id)
    }
    enabled_checks = dict((key, value) for key, value in checks.enabled_checks.items() if value)

    for k, v in enabled_checks.items():
        set_enabled[k] = set_checks[k].check()

    checks.enabled_checks = set_enabled
    checks.score = checks.calc_score()
    checks.filename = filename
    checks.user = user.username
    checks.lms_user_id = user.lms_user_id
    if user.params_for_passback:
        checks.is_passbacked = False

    return checks


# TODO: объединить check и check_report, передавая список проверок
def check_report(parsed_file, checks, filename, user):
    set_checks = {
        "simple_check": ReportSimpleCheck(parsed_file),
        "image_share_check": ReportImageShareCheck(parsed_file)
    }
    # добавить зависимость от критериев проверки
    enabled_checks = set_checks
    check_names = enabled_checks
    set_enabled = dict.fromkeys(check_names, False)

    for k, v in enabled_checks.items():
        set_enabled[k] = set_checks[k].check()

    checks.enabled_checks = set_enabled
    checks.score = checks.calc_score()
    checks.filename = filename
    checks.user = user.username
    checks.lms_user_id = user.lms_user_id
    if user.params_for_passback:
        checks.is_passbacked = False

    return checks
