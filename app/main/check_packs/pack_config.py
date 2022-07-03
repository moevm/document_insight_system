from docx.enum.text import WD_ALIGN_PARAGRAPH

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
    ['future_dev']
]
BASE_REPORT_CRITERION = [
    ["simple_check"],
    ["sections_check", {"header_style_dicts": (
        {
            "bold": True,
            "italic": False,
            "all_caps": True,
            "alignment": WD_ALIGN_PARAGRAPH.CENTER,
            "font_name": "Times New Roman",
            "font_size_pt": 14.0,
            "first_line_indent_cm": 0.0
        },
        {
            "bold": True,
            "italic": False,
            "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
            "font_name": "Times New Roman",
            "font_size_pt": 14.0,
            "first_line_indent_cm": 1.25
        }
    ),
        "header_texts": [[], ["Цель работы.", "Выполнение работы.", "Выводы."]],
        "prechecked_style_props": ["bold", "italic", "all_caps", "alignment"]
    }]
]

BASE_PACKS = {
    'pres': BaseCriterionPack(BASE_PRES_CRITERION, 'pres', min_score=1.0, name="BasePresentationCriterionPack"),
    'report': BaseCriterionPack(BASE_REPORT_CRITERION, 'report', min_score=1.0, name="BaseReportCriterionPack")
}
