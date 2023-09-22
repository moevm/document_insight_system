from .base_criterion_pack import BaseCriterionPack

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
    ['pres_right_words'],
    ['pres_image_share'],
    ['future_dev'],
    ['pres_banned_words_check'],
    ['pres_empty_slide'],
]
BASE_REPORT_CRITERION = [
    ["simple_check"],
    ["banned_words_in_literature"],
    ["page_counter"],
    ["image_share_check"],
    # ["headers_at_page_top_check", {"headers": ["Приложение А Исходный код программы"]}],
    ["headers_at_page_top_check"],
    ["lr_sections_check"],
    ["style_check"],
    ["short_sections_check"],
    ["banned_words_check"],
    ["right_words_check"],
    ["banned_words_in_literature"],
    ["literature_references"],
    ["image_references"],
    ["table_references"],
    ["first_pages_check"],
    ["main_character_check"],
    ["needed_headers_check"],
    ["header_check"],
    ["report_section_component"],
    ["main_text_check"],
    ["spelling_check"]
]

DEFAULT_TYPE = 'pres'
REPORT_TYPES = ('LR', 'VKR')
DEFAULT_REPORT_TYPE_INFO = {'type': 'report', 'report_type': REPORT_TYPES[1]}
DEFAULT_PRES_TYPE_INFO = {'type': 'pres'}
DEFAULT_TYPE_INFO = DEFAULT_PRES_TYPE_INFO

BASE_PACKS = {
    'pres': BaseCriterionPack(BASE_PRES_CRITERION, DEFAULT_PRES_TYPE_INFO, min_score=1.0,
                              name="BasePresentationCriterionPack"),
    'report': BaseCriterionPack(BASE_REPORT_CRITERION, DEFAULT_REPORT_TYPE_INFO, min_score=1.0,
                                name="BaseReportCriterionPack")
}
