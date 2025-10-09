from ..base_check import BaseReportCriterion, answer
from logging import getLogger


logger = getLogger('root')

SW_CONSTANTS = {
    "SW_KEY_QUESTIONS_SECTIONS": {
        "Проблема": {
            "words": 15,
            "sentences": 1
        },
        "Объект исследования": {
            "words": 15,
            "sentences": 1
        },
        "Предмет исследования": {
            "words": 15,
            "sentences": 1
        },
        "Цель дипломного исследования": {
            "words": 30,
            "sentences": 1
        },
        "Цель на текущий семестр": {
            "words": 30,
            "sentences": 1
        }
    },
    "SW_ANALOGS_SECTIONS": {},
    "SW_FINAL_SECTIONS": {},
}


class SWSectionSizeCheck(BaseReportCriterion):
    label = "Проверка объема определенных разделов"
    description = "Проверка объема определенных разделов по количеству предложений и количеству слов"
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
        result = dict.fromkeys(self.sections.keys(), None)
        for chapter in chapters:
            if chapter['name'] in self.sections:
                # get size (count of sentences)
                sentences = list(filter(bool, chapter['text'].split('.')))
                # get size (count of words)
                words = chapter['text'].split()
                result[chapter['name']] = {
                    'sentences': len(sentences) <= self.sections[chapter['name']]['sentences'],
                    'words': len(words) <= self.sections[chapter['name']]['words']
                }
        feedback = ""
        if not all(r['sentences'] for r in result.values()):
            feedback += "<br>Размер следующих разделов не удовлетворяет требованиям <strong>по количеству предложений</strong> (помните, что часть разделов явлются словосочетаниями, а не полным текстом): <br>  - " + \
                '<br>  - '.join(f"'{chapter}' - должен быть не более {self.sections[chapter]['sentences']}" for chapter, check in result.items() if not check['sentences'])
        if not all(r['words'] for r in result.values()):
            feedback += "<br>Размер следующих разделов не удовлетворяет требованиям <strong>по количеству слов</strong> (попробуйте подобрать более ёмкие и короткие формулировки): <br>  - " + \
                '<br>  - '.join(f"'{chapter}' - должен быть не более {self.sections[chapter]['words']}" for chapter, check in result.items() if not check['words'])
               
        if feedback:
            return answer(0, feedback)
        
        return answer(1, "Проверка пройдена!")
