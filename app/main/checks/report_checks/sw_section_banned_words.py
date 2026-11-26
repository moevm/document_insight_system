import re
from copy import deepcopy
from logging import getLogger

from ..base_check import BaseReportCriterion, answer, morph

logger = getLogger('root')

SW_CONSTANTS = {
    "SW_KEY_QUESTIONS_SECTIONS": {"Проблема": {'отсутствие'}},
    "SW_ANALOGS_SECTIONS": {
        "Критерии сравнения аналогов": {
            "документация",
            "локализация",
            "перевод",
            "стоимость",
            "цена",
            "простота",
            "гибкость",
        },
        "Таблица сравнения аналогов": {
            "да",
            "нет",
            "есть",
            "простота",
            "гибкость",
            "простой",
            "слабый",
            "легкий",
            "тяжелый",
            "сильный",
        },
    },
    "SW_FINAL_SECTIONS": {
        "Критерии сравнения аналогов": {
            "документация",
            "локализация",
            "перевод",
            "стоимость",
            "цена",
            "простота",
            "гибкость",
        },
        "Таблица сравнения аналогов": {
            "да",
            "нет",
            "есть",
            "простота",
            "гибкость",
            "простой",
            "слабый",
            "легкий",
            "тяжелый",
            "сильный",
        },
    },
}


class SWSectionBannedWordsCheck(BaseReportCriterion):
    label = "Проверка отсутствия запретных слов в определенных разделах"
    _description = "Проверка отсутствия запретных слов в определенных разделах"
    id = "sw_section_banned_word"

    def __init__(self, file_info, sections_info=None):
        super().__init__(file_info)

        if sections_info is None:
            sections_info = 'SW_KEY_QUESTIONS_SECTIONS'
        if isinstance(sections_info, dict):
            self.sections = deepcopy(sections_info)
        elif isinstance(sections_info, str) and sections_info in SW_CONSTANTS:
            self.sections = deepcopy(SW_CONSTANTS[sections_info])
        else:
            raise ValueError(f'Неизвестная конфигурация разделов: {sections_info!r}')

        for chapter in self.sections:
            self.sections[chapter] = set(morph.normal_forms(word)[0] for word in self.sections[chapter])

        self.warning = not bool(self.sections)

    def check(self):
        if not self.sections:
            return answer(True, 'Правила для выбранных разделов не заданы; критерий не влияет на оценку.')
        if not self.is_markdown:
            return answer(False, 'Критерий предназначен для отчётов Markdown.')

        def check_text(text, banned_words):
            words = {morph.normal_forms(word)[0] for word in re.split(r'[^\w-]+', text)}
            return set(words).intersection(banned_words)

        self.file.make_chapters('VKR')
        chapters = self.file.chapters_to_str()
        self.file.build_chapter_tree(chapters)

        missing = set(self.sections) - {chapter['name'] for chapter in chapters}
        feedback = '<br>Не найдены разделы: ' + ', '.join(sorted(missing)) if missing else ''

        def visit(node, banned_words):
            nonlocal feedback
            found = check_text(node['text'], banned_words)
            if found:
                feedback += f"<br>Раздел '{node['name']}' содержит запрещенные слова {found}"
            for child in node.get('children', []):
                visit(child, banned_words)

        for chapter in chapters:
            if chapter['name'] in self.sections:
                visit(chapter['node'], self.sections[chapter['name']])
        if feedback:
            return answer(0, feedback)

        return answer(1, "Проверка пройдена!")
