from .base_criterion_pack import BaseCriterionPack
from ..checks.report_checks.style_check_settings import StyleCheckSettings

BASE_PRES_CRITERION = [
    ['template_name'],
    ['slides_number', {'slides_number': [10, 12], 'detect_additional': True}],
    ['slides_enum'],
    ['slides_headers'],
    ['find_slides', {'key_slide': 'Цель и задачи'}],
    ['find_slides', {'key_slide': 'Апробация'}],
    ['find_on_slide', {'key_slide': ['Актуальность', 'Актуальности', 'Актуальностью']}],
    ['find_slides', {'key_slide': 'Заключение'}],
    ['slide_every_task', {'min_percent': 70}],
    ['conclusion_actual', {'min_percent': 70}],
    ['future_dev']
]
BASE_REPORT_CRITERION = [
    ["simple_check"],
    ["banned_words_check"],
    ["headers_at_page_top_check", {"headers": ["Приложение А Исходный код программы"]}],
    ["sections_check", {"presets": StyleCheckSettings.LR_CONFIG, "prechecked_props": None}]
]

BASE_PACKS = {
    'pres': BaseCriterionPack(BASE_PRES_CRITERION, 'pres', min_score=1.0, name="BasePresentationCriterionPack"),
    'report': BaseCriterionPack(BASE_REPORT_CRITERION, 'report', min_score=1.0, name="BaseReportCriterionPack")
}
