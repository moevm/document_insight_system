from docx.enum.text import WD_ALIGN_PARAGRAPH


class StyleCheckSettings:
    APPENDIX_UNIFY_REGEX = "(?i)^приложение \\w$"
    APPENDIX_REGEX = "(?i)^ПРИЛОЖЕНИЕ (\\w)\\n(.+)"
    HEADER_1_NUM_REGEX = "^([1-9][0-9]*\\. )([\\w\\s])+$"
    HEADER_2_NUM_REGEX = "^[1-9][0-9]*\\.([1-9][0-9]*\\. )([\\w\\s]+)$"
    HEADER_1_REGEX = "^()([\\w\\s]+)$"
    HEADER_2_REGEX = "^()([\\w\\s]+)\\.$"
    HEADER_1_STYLE = {
        "bold": True,
        "italic": False,
        "all_caps": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 0.0
    }
    HEADER_2_STYLE = {
        "bold": True,
        "italic": False,
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 1.25
    }
    PRECHECKED_PROPS = ["bold", "italic", "all_caps", "alignment"]
    MAIN_TEXT_STYLE = {
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 1.25,
        "line_spacing": 1.5
    }
    LISTING_STYLE = {
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "font_name": "Courier New",
        "font_size_pt": 11.0,
        "first_line_indent_cm": 1.25,  # ????
        "line_spacing": 1.0
    }
    IMAGE_CAPTION_STYLE = {
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 1.25,  # ????
        "line_spacing": 1.5
    }
    TABLE_CAPTION_STYLE = {
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 0.0,
        "line_spacing": 1.0
    }

    # Order of styles may be significant! First level 1, then level 2, if config is used with short_sections_check.
    # Otherwise, order doesn't matter.
    LR_CONFIG = [
        {
            "style": HEADER_1_STYLE,
            "headers": ["Исходный код программы"],
            "unify_regex": APPENDIX_UNIFY_REGEX,
            "regex": APPENDIX_REGEX,
        },
        {
            "style": HEADER_2_STYLE,
            "headers": ["Цель работы", "Основные теоретические положения", "Выполнение работы", "Выводы"],
            "unify_regex": None,
            "regex": HEADER_2_REGEX,
        }
    ]

    LR_MAIN_TEXT_CONFIG = [
        {
            "name": "Основной текст",
            "style": MAIN_TEXT_STYLE
        },
        {
            "name": "Листинг",
            "style": LISTING_STYLE
        },
        {
            "name": "Подпись рисунка",
            "style": IMAGE_CAPTION_STYLE
        },
        {
            "name": "Подпись таблицы",
            "style": TABLE_CAPTION_STYLE
        }
    ]

    CONFIGS = {
        'LR_HEADERS': LR_CONFIG,
        'LR_MAIN_TEXT': LR_MAIN_TEXT_CONFIG
    }
