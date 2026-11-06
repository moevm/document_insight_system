from app.main.reports.section_patterns import INTRODUCTION_TITLE

SECTION_CONFIG = {
    INTRODUCTION_TITLE.lower(): {
        "patterns": [
            'актуальность',
            'объект исследования',
            'предмет исследования',
            'цель работы',
            'задачи',
            'практическая значимость',
        ],
        "bold_check_exceptions": ['актуальность'],
    },
    "default": {"patterns": ['цель', 'задачи'], "bold_check_exceptions": []},
}
