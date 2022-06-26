from ..base_check import BaseCheck, answer
import re
import pymorphy2

morph = pymorphy2.MorphAnalyzer()


class BannedWordsInLiteratureCheck(BaseCheck):
    def __init__(self, file, banned_words=[]):
        super().__init__(file)
        self.banned_words = [morph.normal_forms(word)[0] for word in banned_words]

    def check(self):
        end_page, start_page = self.find_start_and_end_pages()

        if start_page:
            detected_words_dict = self.find_banned_words(end_page, start_page)
        else:
            return answer(False, f'Нет списка литературы')

        if detected_words_dict:
            result_str = ""
            for i in sorted(detected_words_dict.keys()):
                result_str += f"{i}: {detected_words_dict[i]}.<br>"
            return answer(False, f'Есть запрещенные слова в списке источников.<br>{result_str}')
        return answer(True, f"Пройдена!")

    def find_banned_words(self, end_page, start_page):
        detected_words = {}
        literature_counter = 0
        for i in range(start_page, end_page + 1):
            one_page = self.file.pdf_file.text_on_page[i].split('\n')
            first_string, last_string = self.find_first_and_last_strings(one_page)

            for ind in range(first_string + 1, last_string):
                if re.match(f"{literature_counter + 1}.", one_page[ind]):
                    literature_counter += 1
                words_from_str = re.split(r'\W+', one_page[ind])
                words_from_str = [morph.normal_forms(word_from_str)[0] for word_from_str in words_from_str]
                for word in self.banned_words:
                    if word in words_from_str:
                        if literature_counter in detected_words.keys():
                            detected_words[literature_counter] += ", " + word
                        else:
                            detected_words[literature_counter] = word
        return detected_words

    def find_first_and_last_strings(self, one_page):
        first_string = -1
        last_string = len(one_page)
        for j in range(len(one_page)):
            page_lowercase = one_page[j].lower()
            if 'список использованных источников' in page_lowercase \
                    or 'список использованной литературы' in page_lowercase \
                    or 'список литературы' in page_lowercase:
                first_string = j
                break
        for j in range(first_string, len(one_page)):
            if re.search('приложение а[\n .]', one_page[j].lower()):
                last_string = j
                break
        return first_string, last_string

    def find_start_and_end_pages(self):
        start_page = 0
        end_page = self.file.pdf_file.page_count
        for i in self.file.pdf_file.text_on_page.keys():
            lowcase_str = self.file.pdf_file.text_on_page[i].lower()
            if 'список использованных источников' in lowcase_str \
                    or 'список использованной литературы' in lowcase_str \
                    or 'список литературы' in lowcase_str:
                start_page = i
            if re.search('приложение а[\n .]', lowcase_str):
                end_page = i
        return end_page, start_page