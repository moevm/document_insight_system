import re

from logging import getLogger

from ..base_check import BaseReportCriterion, answer, morph


logger = getLogger('root')

SW_CONSTANTS = {
    "SW_KEY_QUESTIONS_SECTIONS": {
        "Проблема": {'отсутствие'}
    },
    "SW_ANALOGS_SECTIONS": {
        "Критерии сравнения аналогов": {"документация", "локализация", "перевод", "стоимость", "цена", "простота", "гибкость"},
        "Таблица сравнения аналогов": {"да", "нет", "есть"}
    },
    "SW_FINAL_SECTIONS": {},
}


class SWSectionBannedWordsCheck(BaseReportCriterion):
    label = "Проверка отсутствия запретных слов в определенных разделах"
    description = "Проверка отсутствия запретных слов в определенных разделах"
    id = "sw_section_banned_word"

    def __init__(self, file_info, sections_info=None):
        super().__init__(file_info)

        self.sections = None
        if sections_info in SW_CONSTANTS:
            self.sections = SW_CONSTANTS[sections_info]
        elif isinstance(sections_info, dict):
            self.sections = sections_info
        for chapter in self.sections:
            self.sections[chapter] = set(morph.normal_forms(word)[0] for word in self.sections[chapter])

    def check(self):
        def check_text(text, banned_words):
            words = {morph.normal_forms(word)[0] for word in re.split(r'[^\w-]+', text)}
            return set(words).intersection(banned_words)
    
        self.file.make_chapters('VKR')
        chapters = self.file.chapters_to_str()
        self.file.build_chapter_tree(chapters)

        feedback = ""
        for chapter in chapters:
            if chapter['name'] in self.sections:
                found_banned_words = check_text(chapter['text'], self.sections[chapter['name']])
                if found_banned_words:
                    feedback += f"<br>Раздел '{chapter['name']}' содержит запрещенные слова {found_banned_words}"
                
                # check subchapters text too
                if chapter['node'].get('children'):
                   for subchapter in chapter['node']['children']:
                        found_banned_words = check_text(subchapter['text'], self.sections[chapter['name']])
                        if found_banned_words:
                            feedback += f"<br>Раздел '{subchapter['name']}' содержит запрещенные слова {found_banned_words}"
        if feedback:
            return answer(0, feedback)

        return answer(1, "Проверка пройдена!")
