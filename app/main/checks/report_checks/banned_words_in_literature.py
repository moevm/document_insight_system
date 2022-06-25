from ..base_check import BaseCheck, answer
import re
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

class BannedWordsInLiteratureCheck(BaseCheck):
    def __init__(self, file, banned_words=[]):
        super().__init__(file)
        self.banned_words = [morph.normal_forms(word)[0] for word in banned_words]

    def check(self):
        start_page = 0
        end_page = self.file.pdf_file.page_count
        for i in self.file.pdf_file.text_on_page.keys():
            lowcase_str = self.file.pdf_file.text_on_page[i].lower()
            if 'список использованных источников' in lowcase_str\
                    or 'список использованной литературы' in lowcase_str\
                    or 'список литературы' in lowcase_str:
                start_page = i
            if re.search('приложение [а-я][\n .]', lowcase_str):
                end_page = i

        if start_page:
            result_dict = {}
            index = 0
            for i in range(start_page,end_page+1):
                one_page = self.file.pdf_file.text_on_page[i].split('\n')
                start = 0
                end = len(one_page)

                for j in range(len(one_page)):
                    page_lower = one_page[j].lower()
                    if 'список использованных источников' in page_lower\
                            or 'список использованной литературы' in page_lower\
                            or 'список литературы' in page_lower:
                        start = j
                        break
                for j in range(start, len(one_page)):
                    if re.search('приложение а[\n .]', one_page[j].lower()):
                        end = j
                        break

                for ind in range(start+1, end):
                    if re.match(f"{index+1}.", one_page[ind]):
                        index += 1
                    words_from_str = re.split(r'[^\w]+', one_page[ind])
                    words_from_str = [morph.normal_forms(word_from_str)[0] for word_from_str in words_from_str]
                    for word in self.banned_words:
                        if word in words_from_str:
                            if index in result_dict.keys():
                                result_dict[index] += ", " + word
                            else:
                                result_dict[index] = word
        else:
            return answer(False, f'Нет списка литературы')

        if result_dict:
            result_str = ""
            for i in sorted(result_dict.keys()):
                result_str += f"{i}: {result_dict[i]}.<br>"
            return answer(False, f'Есть запрещенные слова в списке источников.<br>{result_str}')
        return answer(True, f"Пройдена!")