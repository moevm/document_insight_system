from ..base_check import BaseReportCriterion, answer
import re


class ReferencesToLiteratureCheck(BaseReportCriterion):
    description = "Проверка наличия ссылок на все источники"
    id = 'literature_references'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        start_literature_par= self.find_start_paragraph()
        if start_literature_par:
            number_of_sources = self.count_sources()
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

    def find_start_paragraph(self):
        start_index = 0
        for i in range(len(self.file.paragraphs)):
            text_string = self.file.paragraphs[i].to_string().lower().split('\n')[1]
            if re.fullmatch(r'text\s+список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы).?\s*',
                            text_string):
                start_index = i
                break
        return start_index

    def count_sources(self):
        literature_counter = 0
        start_page, end_page = self.search_literature_start_pdf()
        print(f"start page = {start_page}, end page = {end_page}")
        for i in range(start_page, end_page + 1):
            print(f"i = {i}")
            one_page = self.file.pdf_file.text_on_page[i].split('\n')
            first_string = -1
            last_string = len(one_page)

            for j in range(len(one_page)):
                one_str_lowercase = one_page[j].lower()
                if re.search(r'\s+список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы).?\s*\n',
                             one_str_lowercase):
                    first_string = j
                    break
            for j in range(first_string, len(one_page)):
                if re.search('приложение а[\n .]', one_page[j].lower()):
                    last_string = j
                    break

            for ind in range(first_string + 1, last_string):
                if re.match(f"{literature_counter + 1}.", one_page[ind]):
                    literature_counter += 1
        return literature_counter

    def search_literature_start_pdf(self):
        start_page = 0
        end_page = self.file.pdf_file.page_count
        for i in self.file.pdf_file.text_on_page.keys():
            lowercase_str = self.file.pdf_file.text_on_page[i].lower()
            if re.search(r'\s*список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы).?\s*',
                         lowercase_str):
                start_page = i
            if re.search('приложение а[\n .]', lowercase_str):
                end_page = i
                break
        return start_page, end_page
