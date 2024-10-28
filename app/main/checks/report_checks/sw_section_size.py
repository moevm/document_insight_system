from ..base_check import BaseReportCriterion, answer
from logging import getLogger


logger = getLogger('root')

SW_CONSTANTS = {
    "SW_KEY_QUESTIONS_SECTIONS": {
        "Проблема": 1,
        "Объект исследования": 1,
        "Предмет исследования": 1,
        "Цель": 1
    },
    "SW_ANALOGS_SECTIONS": {},
    "SW_FINAL_SECTIONS": {},
}


class SWSectionSizeCheck(BaseReportCriterion):
    label = "Проверка объема определенных разделов"
    description = "Проверка объема определенных разделов"
    id = "sw_sections_size_check"
    priority = True

    def __init__(self, file_info, sections_info=None):
        super().__init__(file_info)
        
        self.sections = None
        if sections_info in SW_CONSTANTS:
            self.sections = SW_CONSTANTS[sections_info]
        elif isinstance(sections_info, dict):
            self.sections = sections_info
    
    def check(self):
        self.file.make_chapters('VKR')
        chapters = self.file.chapters_to_str()
        result = dict.fromkeys(self.sections.keys(), False)
        for chapter in chapters:
            if chapter['name'] in self.sections:
                # check size (count of sentences)
                sentences = list(filter(bool, chapter['text'].split('.')))
                if len(sentences) <= self.sections[chapter['name']]:
                    result[chapter['name']] = True
        if not all(result.values()):
            feedback = "Размер следующих разделов не удовлетворяет требованиям (размер указан в предложениях): " + \
                ', '.join(f"'{chapter}' - должен быть {self.sections[chapter]}" for chapter, check in result.items() if not check)
            return answer(0, feedback)
        
        return answer(1, "Проверка пройдена!")
