from docx.enum.text import WD_ALIGN_PARAGRAPH


class StyleCheckSettings:
    APPENDIX_UNIFY_REGEX = r"(?i)^приложение \w$"
    APPENDIX_REGEX = r"(?i)^ПРИЛОЖЕНИЕ (\w)\n(.+)"
    HEADER_1_NUM_REGEX = r"^([1-9][0-9]*\ )([\w\s])+$"
    HEADER_2_NUM_REGEX = r"^[1-9][0-9]*\.([1-9][0-9]*\ )([\w\s]+)$"
    HEADER_NUM_REGEX = r"^\d.+$"
    HEADER_REGEX = r"^\D+.+$"
    HEADER_1_REGEX = r"^([1-9][0-9]*\.([1-9][0-9]*\.))?\s*.+$"
    HEADER_2_REGEX = r"^([1-9][0-9]*\.([1-9][0-9]*\.)*)?\s*.+$"
    STD_BANNED_WORDS = ('мы', 'моя', 'мои', 'моё', 'наш', 'наши',
        'аттач', 'билдить', 'бинарник', 'валидный', 'дебаг', 'деплоить', 'десктопное', 'железо',
        'исходники', 'картинка', 'консольное', 'конфиг', 'кусок', 'либа', 'лог', 'мануал',
        'отнаследованный', 'парсинг', 'пост', 'распаковать', 'сбоит', 'скачать', 'склонировать', 'скрипт',
        'тестить', 'тул', 'тула', 'тулза', 'фиксить', 'флажок', 'флаг', 'юзкейс', 'продакт', 'продакшн',
        'прод', 'фидбек', 'дедлайн', 'дэдлайн', 'оптимально', 'надежный', 'интуитивный',
        'хороший', 'плохой', 'идеальный', 'быстро', 'медленно', 'какой-нибудь', 'некоторый', 'почти'
    )
    STD_WARNED_WORDS = ('машина', 'оптимальный') # TODO: list of "warning" words
    STD_MIN_LIT_REF = 1
    STD_MAX_LIT_REF = 1000 #just in case for future edit
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
    HEADER_1_NUM_STYLE = {
        "bold": True,
        "italic": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 1.25
    }
    HEADER_2_NUM_STYLE = {
        "bold": True,
        "italic": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 1.25
    }
    PRECHECKED_PROPS = ["bold", "italic", "all_caps", "alignment"]
    PRECHECKED_PROPS_2 = ["bold", "italic", "all_caps", "alignment", "font_name", "font_size_pt"]
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
    TABLE_CAPTION_STYLE_VKR = {
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 0.0,
        "line_spacing": 1.0
    }

    # Order of styles may be significant! First level 1, then level 2 and so on.
    LR_CONFIG = {
        'any_header':
        {
            "style": HEADER_2_STYLE,
            "docx_style": ["heading 2", "heading 3", "heading 4"],
            "headers": ["Цель работы", "Выполнение работы", "Выводы"],
            "unify_regex": HEADER_2_REGEX,
            "regex": HEADER_2_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
            'min_ref_for_literature_references_check': STD_MIN_LIT_REF,
            'mах_ref_for_literature_references_check': STD_MAX_LIT_REF
        }
    }

    VKR_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", "ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"],
            "chapters_for_lit_ref": {},
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
            'min_ref_for_literature_references_check': STD_MIN_LIT_REF,
            'mах_ref_for_literature_references_check': STD_MAX_LIT_REF
        },
        'first_header':
        {
            "style": HEADER_1_NUM_STYLE,
            "docx_style": ["heading 2"], 
            "headers": [],
            "unify_regex": None,
            "regex": HEADER_1_NUM_REGEX,
        },
        'second_header':
        {
            "style": HEADER_2_NUM_STYLE,
            "docx_style": ["heading 3", "heading 4"],
            "headers": [],
            "unify_regex": None,
            "regex": HEADER_2_REGEX,
        }
    }

    NIR1_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["ВВЕДЕНИЕ", "ПОСТАНОВКА ЗАДАЧИ", "ОБЗОР ЛИТЕРАТУРЫ", "ВЫВОДЫ",
                        "ПЛАН РАБОТЫ НА ВЕСЕННИЙ СЕМЕСТР", "ОТЗЫВ РУКОВОДИТЕЛЯ", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS + ('доработать', 'доработка', 'переписать', 'рефакторинг', 'исправление'),
            "warned_words": STD_WARNED_WORDS
        },
    }

    NIR2_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["ВВЕДЕНИЕ", "ПОСТАНОВКА ЗАДАЧИ", "РЕЗУЛЬТАТЫ РАБОТЫ В ВЕСЕННЕМ СЕМЕСТРЕ", "ОПИСАНИЕ ПРЕДПОЛАГАЕМОГО МЕТОДА РЕШЕНИЯ",
                        "ПЛАН РАБОТЫ НА ОСЕННИЙ СЕМЕСТР", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS + ('доработать', 'доработка', 'переписать', 'рефакторинг', 'исправление'),
            "warned_words": STD_WARNED_WORDS
        },
    }

    NIR3_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["ВВЕДЕНИЕ", "ПОСТАНОВКА ЗАДАЧИ", "РЕЗУЛЬТАТЫ РАБОТЫ В ОСЕННЕМ СЕМЕСТРЕ", "ОПИСАНИЕ ПРЕДПОЛАГАЕМОГО МЕТОДА РЕШЕНИЯ",
                        "ПЛАН РАБОТЫ НА ВЕСЕННИЙ СЕМЕСТР", "ОТЗЫВ РУКОВОДИТЕЛЯ", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS + ('доработать', 'доработка', 'переписать', 'рефакторинг', 'исправление'),
            "warned_words": STD_WARNED_WORDS
        },
    }

    MD_CONFIG = {
        'Задание 1':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Поставленная цель и задачи",
                        "Тематика статьи",
                        "Методы обоснования",
                        "Статья",
                        ],
            "chapters_for_lit_ref": {},
            "header_for_report_section_component": "Поставленная цель и задачи",
            "headers_for_lit_count": [],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
        },
        'Задание 2':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Характеристика используемых данных",
                        "Характеристика выводов",
                        "Статья",
                        ],
            "chapters_for_lit_ref": {},
            "header_for_report_section_component": "",
            "headers_for_lit_count": [],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
        }
        }

    OPNP_CONFIG = {
        'Ответы на ключевые вопросы':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Проблема",
                        "Актуальность",
                        "Объект исследования",
                        "Предмет исследования",
                        "Цель дипломного исследования",
                        "Цель на текущий семестр",
                        "Задачи",
                        "Список использованных источников"
                        ],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_ref_for_literature_references_check': 1,
            'mах_ref_for_literature_references_check': 1000, #just for future possible edit
            'min_count_for_banned_words_check': 2,
            'max_count_for_banned_words_check': 10
        },
        'Сравнение аналогов':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Принцип отбора аналогов",
                        "Критерии сравнения аналогов",
                        "Выводы по итогам сравнения",
                        "Выбор метода решения",
                        "Список использованных источников"
                        ],
            "chapters_for_lit_ref": {},
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_ref_for_literature_references_check': 3,
            'mах_ref_for_literature_references_check': 1000, #just for future possible edit
            'min_count_for_banned_words_check': 2,
            'max_count_for_banned_words_check': 10
        },
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Аннотация",
                        "Введение",
                        "Обзор предметной области",
                        "Выбор метода решения",
                        "Заключение",
                        "Список использованных источников"
                        ],
            "chapters_for_lit_ref": {},
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": STD_BANNED_WORDS,
            "warned_words": STD_WARNED_WORDS,
            'min_ref_for_literature_references_check': 5,
            'mах_ref_for_literature_references_check': 1000, #just for future possible edit
            'min_count_for_banned_words_check': 2,
            'max_count_for_banned_words_check': 10
        }

    }


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
            "name": "вкр_подпись для рисунков",
            "style": IMAGE_CAPTION_STYLE
        },
        {
            "name": "вкр_подпись таблицы",
            "style": TABLE_CAPTION_STYLE_VKR
        }
    ]

    VKR_MAIN_TEXT_CONFIG = [
        {
            "name": "body text",
            "style": MAIN_TEXT_STYLE
        },
        {
            "name": "листинг",
            "style": LISTING_STYLE
        },
        {
            "name": "вкр_подпись для рисунков",
            "style": IMAGE_CAPTION_STYLE
        },
        {
            "name": "вкр_подпись таблицы",
            "style": TABLE_CAPTION_STYLE_VKR
        }
    ]

    CONFIGS = {
        'LR_HEADERS': LR_CONFIG,
        'LR_MAIN_TEXT': LR_MAIN_TEXT_CONFIG,
        'VKR_HEADERS': VKR_CONFIG,
        'VKR_MAIN_TEXT': VKR_MAIN_TEXT_CONFIG,
        'NIR_HEADERS': NIR2_CONFIG,
        'NIR1_HEADERS': NIR1_CONFIG,
        'NIR2_HEADERS': NIR2_CONFIG,
        'NIR3_HEADERS': NIR3_CONFIG,
        'MD_HEADERS' : MD_CONFIG,
        'OPNP_HEADERS' : OPNP_CONFIG,
    }
