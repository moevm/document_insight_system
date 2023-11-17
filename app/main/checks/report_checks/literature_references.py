import re

from ..base_check import BaseReportCriterion, answer


class ReferencesToLiteratureCheck(BaseReportCriterion):
    description = "Проверка наличия ссылок на все источники"
    id = 'literature_references'

    def __init__(self, file_info, min_ref=1, max_ref=1000):
        super().__init__(file_info)
        self.headers = []
        self.literature_header = []
        self.name_pattern = r'список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы)'
        self.min_ref = min_ref
        self.max_ref = max_ref

    def late_init_vkr(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.literature_header = self.file.find_literature_vkr(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        number_of_sources = 0
        start_literature_par = 0
        result_str = ''
        if self.file_type['report_type'] == 'LR':
            start_literature_par = self.find_start_paragraph()
            if start_literature_par:
                number_of_sources = self.count_sources()
            else:
                return answer(False, f'Нет списка литературы.')
        elif self.file_type['report_type'] == 'VKR':
            self.late_init_vkr()
            header = self.literature_header
            if not header:
                return answer(False,
                              f'Не найден Список использованных источников.<br><br>Проверьте корректность использования стилей.')
            start_literature_par = header["number"]
            number_of_sources = self.count_sources_vkr(header)
        else:
            return answer(False, 'Во время обработки произошла критическая ошибка')
        if not number_of_sources:
            return answer(False,
                          f'В Списке использованных источников не найдено ни одного источника.<br><br>Проверьте корректность использования нумированного списка.')
        references = self.search_references(start_literature_par)
        all_numbers = set()
        for i in range(1, number_of_sources + 1):
            all_numbers.add(i)
        if len(references.symmetric_difference(all_numbers)) == 0:
            if not self.min_ref <= number_of_sources <= self.max_ref:
                return answer(False, f'Список источников оформлен верно, однако их количество ({number_of_sources}) не удовлетворяет необходимому критерию. <br> Количество источников должно быть от {self.min_ref} до {self.max_ref}.')
            else:
                return answer(True, f"Пройдена!")
        elif len(references.difference(all_numbers)):
            if len(all_numbers.difference(references)) == 0:
                references -= all_numbers
                result_str += f'Упомянуты несуществующие источники: {", ".join(str(num) for num in sorted(references))} <br> Всего источников: {number_of_sources}<br><br>'
            else:
                extras = references - all_numbers
                unnamed = all_numbers - references
                result_str += f'Упомянуты несуществующие источники: {", ".join(str(num) for num in sorted(extras))} <br> А также упомянуты не все источники: {", ".join(str(num) for num in sorted(unnamed))} <br> Всего источников: {number_of_sources}<br><br>'
        else:
            all_numbers -= references
            result_str = f'Упомянуты не все источники из списка.<br>Список источников без упоминания: {", ".join(str(num) for num in sorted(all_numbers))} <br> Всего источников: {number_of_sources}<br><br>'
        result_str += '''
                    Если возникли проблемы, попробуйте сделать следующее:
                    <ul>
                        <li>Убедитесь, что для ссылки на источник используются квадратные скобки;</li>
                        <li>Убедитесь, что для оформления списка литературы был использован нумированный список;</li>
                        <li>Убедитесь, что после и перед нумированным списком отсутствуют непустые абзацы.</li>
                    </ul>
                    '''
        return answer(False, result_str)

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
            if re.fullmatch(self.name_pattern, text_string):
                start_index = i
                break
        return start_index

    def count_sources_vkr(self, header):
        literature_counter = 0
        if not len(header["child"]):
            return literature_counter
        for child in header["child"]:
            if child["text"].startswith('ПРИЛОЖЕНИЕ'):
                break
            # if re.search(f"дата обращения", child["text"].lower()):
            literature_counter += 1
        return literature_counter

    def count_sources(self):
        literature_counter = 0
        start_page, end_page = self.search_literature_start_pdf()
        for i in range(start_page, end_page + 1):
            one_page = self.file.pdf_file.text_on_page[i].split('\n')
            first_string = -1
            last_string = len(one_page)

            for j in range(len(one_page)):
                one_str_lowercase = one_page[j].lower()
                if re.search(self.name_pattern, one_str_lowercase):
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
            if re.search(self.name_pattern, lowercase_str):
                start_page = i
            if re.search('приложение а[\n .]', lowercase_str):
                end_page = i
                break
        return start_page, end_page