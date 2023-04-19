import re

from ..base_check import BaseReportCriterion, answer, morph


class BannedWordsInLiteratureCheck(BaseReportCriterion):
    description = "Проверка наличия запрещенных слов в списке литературы"
    id = 'banned_words_in_literature'

    def __init__(self, file_info, banned_words=["wikipedia"]):
        super().__init__(file_info)
        self.headers_page = 1
        self.literature_header = []
        self.banned_words = [morph.normal_forms(word)[0] for word in banned_words]
        self.name_pattern = r'список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы)'

    def late_init_vkr(self):
        self.literature_header = self.file.find_literature_vkr(self.file_type['report_type'])
        self.headers_page = self.file.find_header_page(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        detected_words_dict = {}
        if self.file_type['report_type'] == 'LR':
            list_of_literature = self.find_literature()
            if len(list_of_literature) == 0:
                return answer(False, f"Нет списка литературы!")
            detected_words_dict = self.find_banned_words(list_of_literature)
        elif self.file_type['report_type'] == 'VKR':
            self.late_init_vkr()
            header = self.literature_header
            if not header:
                return answer(False, f"Нет списка использованных источников!")
            if not header["child"]:
                return answer(False, "Не найдено ни одного источника.")
            header_number = header["number"]
            for child in header["child"]:
                child_number = child["number"] - header_number
                words = re.split(r'\W+', child["text"])
                words = [morph.normal_forms(word)[0] for word in words]
                for banned_word in self.banned_words:
                    if banned_word in words:
                        if child_number in detected_words_dict.keys():
                            detected_words_dict[child_number] += ", " + banned_word
                        else:
                            detected_words_dict[child_number] = banned_word
        else:
            return answer(False, 'Во время обработки произошла критическая ошибка')
        if detected_words_dict:
            result_str = ""
            for i in sorted(detected_words_dict.keys()):
                result_str += f"Абзац {i}: {detected_words_dict[i]}.<br>"
            return answer(False, f'Есть запрещенные слова в списке источников '
                                 f'{self.format_page_link([self.headers_page])}:<br><br>{result_str}')
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
