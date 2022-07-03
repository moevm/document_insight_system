from ..base_check import BaseReportCriterion, answer
import re


class ReferencesToLiteratureCheck(BaseReportCriterion):
    description = "Проверка наличия ссылок на все источники"
    id = 'literature_references'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        start_literature_par, end_literature_par, empty_strings = self.find_start_and_end_paragraphs()
        if start_literature_par:
            number_of_sources = end_literature_par - start_literature_par - empty_strings - 1
            references = self.search_references(start_literature_par)
            if len(references) == number_of_sources:
                return answer(True, f"Пройдена!")
            else:
                all_numbers = set()
                for i in range(1, number_of_sources + 1):
                    all_numbers.add(i)
                all_numbers -= references
                return answer(False,
                              f'Упомянуты не все источники из списка <br> Список источников без упоминания: {", ".join(str(q) for q in sorted(all_numbers))}')
        else:
            return answer(False, f'Нет списка литературы')

    def search_references(self, start_par):
        array_of_references = set()
        for i in range(0, start_par):
            detected_references = re.findall(r'\[[\d \-,]+\]', self.file.paragraphs[i].to_string().split('\n')[1])
            if detected_references:
                for reference in detected_references:
                    for one_part in re.split(r'[\[\],]', reference):
                        if re.match(r'\d+[ \-]+\d+', one_part):
                            start, end = re.split(r'[ -]+', one_part)
                            for k in range(int(start), int(end) + 1):
                                array_of_references.add(k)
                        elif one_part != '':
                            array_of_references.add(int(one_part))
        return array_of_references

    def find_start_and_end_paragraphs(self):
        start_index = 0
        end_index = len(self.file.paragraphs)
        empty_strings = 0
        for i in range(len(self.file.paragraphs)):
            text_string = self.file.paragraphs[i].to_string().lower().split('\n')[1]
            if re.fullmatch(r'text\s+список использованных источников[\s.]+', text_string) or \
                    re.fullmatch(r'text\s+список использованной литературы[\s.]+', text_string) or \
                    re.fullmatch(r'text\s+список литературы[\s.]+', text_string):
                start_index = i
                break
        if start_index:
            for i in range(start_index, len(self.file.paragraphs)):
                text_string = self.file.paragraphs[i].to_string().lower().split('\n')[1]
                if re.fullmatch(r'text[\s\\t]+', text_string):
                    empty_strings += 1
                if re.fullmatch(r'text\s+приложение а.?\s*', text_string):
                    end_index = i
                    break
        return start_index, end_index, empty_strings
