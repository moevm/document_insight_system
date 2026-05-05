class ReportMainPageSetting:
    FIRST_TABLE_GENERAL = [
        {"key": "Факультет", "found_value": 0, "found_key": 0, "find": 1, "value": ["КТИ"], "logs": ""},
        {"key": "Кафедра", "found_value": 0, "found_key": 0, "find": 1, "value": ["МО ЭВМ"], "logs": ""},
        {"key": "Зав. кафедрой", "found_value": 0, "found_key": 0, "find": 3, "value": ["А.А. Лисс"], "logs": ""},
    ]
    FIRST_TABLE_DEGREE_PART = {
        "bsc": [
            {
                "key": "Направление",
                "found_value": 0,
                "found_key": 0,
                "find": 1,
                "value": [
                    "01.03.02 Прикладная математика и информатика",
                    "09.03.04 Программная инженерия",
                ],
                "logs": "",
            },
            {
                "key": "Профиль",
                "found_value": 0,
                "found_key": 0,
                "find": 1,
                "value": [
                    "Математическое обеспечение программно-информационных систем",
                    "Разработка программно-информационных систем",
                ],
                "logs": "",
            },
        ],
        "msc": [
            {
                "key": "Направление",
                "found_value": 0,
                "found_key": 0,
                "find": 1,
                "value": [
                    "09.04.04 Программная инженерия",
                ],
                "logs": "",
            },
            {
                "key": "Программа",
                "found_value": 0,
                "found_key": 0,
                "find": 1,
                "value": [
                    "Разработка распределенных программных систем",
                    "Математическое и программное обеспечение систем искусственного интеллекта",
                    "Автономные интеллектуальные системы"
                ],
                "logs": "",
            },
        ]
    }
    SECOND_TABLE = [
        {
            "key": "Руководитель",
            "found_value": 0,
            "found_key": 0,
            "find": 3,
            "value": [r"(Руководитель).*([кд]\..+\.н\., (доцент|профессор))[|]*([А-Я]\.[А-Я]\. [А-Я][а-я]+)"],  #
            "logs": "",
        },
        {
            "key": "Консультант",
            "found_value": 0,
            "found_key": 0,
            "find": 1,
            "value": [
                r"[кд]\..+\.н\., (доцент|профессор)"
            ],  # (Консультант).*(([кд]\..+\.н\., (доцент|профессор))|).*([А-Я]\.[А-Я]\. [А-Я][а-я]+)
            # (([кд]\..+\.н\., (доцент|профессор))|)[|]*([А-Я]\.[А-Я]\. [А-Я][а-я]+)
            "logs": "",
        },
    ]

    @classmethod
    def get_first_table(cls, edu_degree='bsc'):
        return cls.FIRST_TABLE_DEGREE_PART[edu_degree] + cls.FIRST_TABLE_GENERAL
