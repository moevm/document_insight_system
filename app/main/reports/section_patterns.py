"""Shared report section names and patterns; callers choose search/match/fullmatch."""

CONTENTS_TITLE = 'Содержание'
APPENDIX_TITLE = 'ПРИЛОЖЕНИЕ'
ABBREVIATIONS_TITLE = 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ'

LITERATURE_PATTERN = r'список\s+(?:использованных\s+|использованной\s+)?(?:источников|литературы)'
# Legacy inline matching also accepts missing spaces (unlike a standalone heading).
LITERATURE_INLINE_PATTERN = r'список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы)'
BODY_END_PATTERN = rf'{LITERATURE_PATTERN}|^{APPENDIX_TITLE}'
BODY_END_PREFIX_PATTERN = rf'{APPENDIX_TITLE}|{LITERATURE_PATTERN}'
CONTENTS_STYLE_PATTERN = rf'(?:toc|{CONTENTS_TITLE.lower()})\s*\d+'
CONTENTS_PAGE_SUFFIX_PATTERN = r'[\s.\d…]+'
APPENDIX_PAGE_PATTERN = rf'{APPENDIX_TITLE} [А-Я]'
APPENDIX_A_PATTERN = rf'{APPENDIX_TITLE.lower()} а[\n .]'

INTRODUCTION_TITLE = 'Введение'
CONCLUSION_TITLE = 'Заключение'
LITERATURE_TITLE = 'Список использованных источников'
REFERAT_TITLE = 'Реферат'
ABSTRACT_TITLE = 'Abstract'
LITERATURE_MD_PATTERN = r'список\s+(?:использованных\s+)?(?:источников|литературы)'
APPENDIX_UNIFY_PATTERN = r'(?i)^приложение \w$'
APPENDIX_MULTILINE_PATTERN = r'(?i)^ПРИЛОЖЕНИЕ (\w)\n(.+)'
INTRODUCTION_CASE_PATTERN = rf'({INTRODUCTION_TITLE.upper()}|{INTRODUCTION_TITLE}|{INTRODUCTION_TITLE.lower()})'
CONCLUSION_CASE_PATTERN = rf'({CONCLUSION_TITLE.upper()}|{CONCLUSION_TITLE}|{CONCLUSION_TITLE.lower()})'
ABBREVIATIONS_CASE_PATTERN = (
    rf'({ABBREVIATIONS_TITLE}|{ABBREVIATIONS_TITLE.capitalize()}|{ABBREVIATIONS_TITLE.lower()})'
)
APPENDIX_CASE_PATTERN = rf'({APPENDIX_TITLE.capitalize()}|{APPENDIX_TITLE}|{APPENDIX_TITLE.lower()}) [А-ЯЁа-яё]'
