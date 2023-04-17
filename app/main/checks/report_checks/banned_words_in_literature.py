import re

from ..base_check import BaseReportCriterion, answer, morph


class BannedWordsInLiteratureCheck(BaseReportCriterion):
    description = "Проверка на наличие запрещенных слов в списке литературы"
    id = 'banned_words_in_literature'

    def __init__(self, file_info, banned_words=[]):
        super().__init__(file_info)
        self.name_pattern = r'text\s+список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы)'
        self.banned_words = [morph.normal_forms(word)[0] for word in banned_words]

    def check(self):
        list_of_literature = self.find_literature()
        if len(list_of_literature) == 0:
            return answer(False, f"Нет списка литературы!")
        detected_words_dict = self.find_banned_words(list_of_literature)
        if detected_words_dict:
            result_str = ""
            for i in sorted(detected_words_dict.keys()):
                result_str += f"{i}: {detected_words_dict[i]}.<br>"
            return answer(False, f'Есть запрещенные слова в списке источников.<br>{result_str}')
        return answer(True, f"Пройдена!")

    def find_banned_words(self, list_of_literature):
        detected_words = {}
        for i in range(len(list_of_literature)):
            words_from_str = re.split(r'\W+', list_of_literature[i])
            words_from_str = [morph.normal_forms(word_from_str)[0] for word_from_str in words_from_str]
            for word in self.banned_words:
                if word in words_from_str:
                    if i in detected_words.keys():
                        detected_words[i] += ", " + word
                    else:
                        detected_words[i] = word
        return detected_words

    def find_literature(self):
        result = []
        start_index = self.start_of_literature_chapter()
        if start_index:
            for i in range(start_index, len(self.file.paragraphs)):
                text_string = self.file.paragraphs[i].to_string().lower().split('\n')[1]
                result.append(text_string)
                if re.fullmatch(r'text\s+приложение а[.\s]+', text_string):
                    break
        return result

    def start_of_literature_chapter(self, ):
        start_index = 0
        for i in range(len(self.file.paragraphs)):
            text_string = self.file.paragraphs[i].to_string().lower().split('\n')[1]
            if re.fullmatch(self.name_pattern, text_string):
                start_index = i
        return start_index
