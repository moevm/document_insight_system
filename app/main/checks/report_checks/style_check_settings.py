from docx.enum.text import WD_ALIGN_PARAGRAPH


class StyleCheckSettings:
    EMPTY_MARKERS = ["" for _ in range(5000)]
    APPENDIX_MARKERS = \
        [chr(n) for n in range(ord("А"), ord("Я") + 1) if chr(n) not in ["З", "Й", "О", "Ч", "Ъ", "Ы", "Ь"]]
    NUM_MARKERS = ["{0}. ".format(i) for i in range(1, 100)]
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

    LR_CONFIG = [
        {
            "style": HEADER_2_STYLE,
            "headers": ["Цель работы", "Основные теоретические положения", "Выполнение работы", "Выводы"],
            "unify_regex": None,
            "regex": HEADER_2_REGEX,
            "markers": EMPTY_MARKERS
        },
        {
            "style": HEADER_1_STYLE,
            "headers": ["Исходный код программы"],
            "unify_regex": APPENDIX_UNIFY_REGEX,
            "regex": APPENDIX_REGEX,
            "markers": APPENDIX_MARKERS
        }
    ]
