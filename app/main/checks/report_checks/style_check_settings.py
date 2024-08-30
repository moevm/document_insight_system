from docx.enum.text import WD_ALIGN_PARAGRAPH


class StyleCheckSettings:
    APPENDIX_UNIFY_REGEX = "(?i)^приложение \\w$"
    APPENDIX_REGEX = "(?i)^ПРИЛОЖЕНИЕ (\\w)\\n(.+)"
    HEADER_1_NUM_REGEX = "^([1-9][0-9]*\\ )([\\w\\s])+$"
    HEADER_2_NUM_REGEX = "^[1-9][0-9]*\\.([1-9][0-9]*\\ )([\\w\\s]+)$"
    HEADER_NUM_REGEX = "^\\d.+$"
    HEADER_REGEX = "^\\D+.+$"
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
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "font_name": "Times New Roman",
        "font_size_pt": 14.0,
        "first_line_indent_cm": 1.25,
        "line_spacing": 1.0
    }

    # Order of styles may be significant! First level 1, then level 2 and so on.
    LR_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 1"],
            "headers": ["Исходный код программы"],
            "unify_regex": APPENDIX_UNIFY_REGEX,
            "regex": APPENDIX_REGEX,
            "banned_words": ['мы'],
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
        },
        'second_header':
        {
            "style": HEADER_2_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Цель работы", "Выполнение работы", "Выводы"],
            "unify_regex": None,
            "regex": HEADER_1_REGEX,
        }
    }

    VKR_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": ['мы'],
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
        },
        'second_header':
        {
            "style": HEADER_1_NUM_STYLE,
            "docx_style": ["heading 2", "heading 3", "heading 4"],
            "headers": [],
            "unify_regex": None,
            "regex": HEADER_NUM_REGEX,
        }
    }
    
    NIR_CONFIG = {
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["ПОСТАНОВКА ЗАДАЧИ", "РЕЗУЛЬТАТЫ РАБОТЫ В ВЕСЕННЕМ СЕМЕСТРЕ", "ОПИСАНИЕ ПРЕДПОЛАГАЕМОГО МЕТОДА РЕШЕНИЯ",
                        "ПЛАН РАБОТЫ НА ОСЕННИЙ СЕМЕСТР", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"],
            "unify_regex": None,
            "regex": HEADER_REGEX,
        },
        'second_header':
        {
            "style": HEADER_1_NUM_STYLE,
            "docx_style": ["heading 3", "heading 4"],
            "headers": ["ПЛАН", "РЕЗУЛЬТАТЫ"],
            "unify_regex": None,
            "regex": HEADER_NUM_REGEX
        }
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
            "header_for_report_section_component": "Поставленная цель и задачи",
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": ['мы'],
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
            "header_for_report_section_component": "",
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": ['мы'],
            'min_count_for_banned_words_check': 3,
            'max_count_for_banned_words_check': 6,
        }
        }

        # },'':
        # {
        #     "style": HEADER_1_NUM_STYLE,
        #     "docx_style": ["heading 2", "heading 3", "heading 4"],
        #     "headers": [],
        #     "unify_regex": None,
        #     "regex": HEADER_NUM_REGEX
        # },'':
        # {
        #     "style": "Main_header",
        #     "docx_style": ["heading 1"],
        #     "headers": ["Задание"],
        #     "unify_regex": None,
        #     "regex": HEADER_NUM_REGEX
        # }


    OPNP_CONFIG = {
        'Сравнение аналогов':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Принцип отбора аналогов",
                        "Критерии сравнения аналогов",
                        "Выводы по итогам сравнения",
                        "Выбор метода решения",
                        ],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": ['аттач', 'билдить', 'бинарник', 'валидный', 'дебаг', 'деплоить', 'десктопное', 'железо',
                             'исходники', 'картинка', 'консольное', 'конфиг', 'кусок', 'либа', 'лог', 'мануал', 'машина',
                             'отнаследованный', 'парсинг', 'пост', 'распаковать', 'сбоит', 'скачать', 'склонировать', 'скрипт',
                             'тестить', 'тул', 'тула', 'тулза', 'фиксить', 'флажок', 'флаг', 'юзкейс', 'продакт', 'продакшн',
                             'прод', 'фидбек', 'дедлайн', 'дэдлайн'],
            'min_ref_for_literature_references_check': 5,
            'mах_ref_for_literature_references_check': 1000, #just for future possible edit
            'min_count_for_banned_words_check': 0,
            'max_count_for_banned_words_check': 0
        },
        'any_header':
        {
            "style": HEADER_1_STYLE,
            "docx_style": ["heading 2"],
            "headers": ["Аннотация",
                        "Введение",
                        "Обзор предметной области == Сравнение аналогов",
                        "Выбор метода решения",
                        "Заключение",
                        "Список литературы"
                        ],
            "unify_regex": None,
            "regex": HEADER_REGEX,
            "banned_words": ['оптимально', 'оптимальный', 'надежный', 'интуитивный'],
            'min_ref_for_literature_references_check': 5,
            'mах_ref_for_literature_references_check': 1000, #just for future possible edit
            'min_count_for_banned_words_check': 0,
            'max_count_for_banned_words_check': 0
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
            "name": "Подпись рисунка",
            "style": IMAGE_CAPTION_STYLE
        },
        {
            "name": "Подпись таблицы",
            "style": TABLE_CAPTION_STYLE
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
        'NIR_HEADERS': NIR_CONFIG,
        'MD_HEADERS' : MD_CONFIG,
        'OPNP_HEADERS' : OPNP_CONFIG,
    }
