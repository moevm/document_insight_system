import re
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class Header:
    msg = ''
    output = True
    __check_results = dict()
    default_header_criteria = {
        '1': {
            'font_name': ['Times New Roman'],
            'font_size': [14],
            'alignment': [WD_PARAGRAPH_ALIGNMENT.CENTER],
            'first_line_indent': [0, None],
            'line_spacing': [1.5],
            'bold': [True],
            'italic': [False, None],
            'underline': [False, None]
        },
        '2': {
            'font_name': ['Times New Roman'],
            'font_size': [14],
            'alignment': [WD_PARAGRAPH_ALIGNMENT.JUSTIFY],
            'first_line_indent': [1.25],
            'line_spacing': [1.5],
            'bold': [True],
            'italic': [False, None],
            'underline': [False, None]
        },
        '3': {
            'font_name': ['Times New Roman'],
            'font_size': [14],
            'alignment': [WD_PARAGRAPH_ALIGNMENT.LEFT],
            'first_line_indent': [1.25],
            'line_spacing': [1.5],
            'bold': [True],
            'italic': [False, None],
            'underline': [False, None]
        }
    }

    def __init__(self, page_objects):
        self.page_objects = page_objects

    def CheckHeader(self):
        application_pattern = r"(Приложение|ПРИЛОЖЕНИЕ|приложение) [А-ЯЁа-яё]"
        third_level_pattern = r"([1-9]\.( ){0,1}){2,}"
        for page in self.page_objects:
            if page.header == 'Титульный лист':
                continue
            self.__check_results[page.header] = dict.fromkeys(self.default_header_criteria['1'].keys(), True)
            if re.search(application_pattern, page.pageObjects[0].text):
                self.Check_Criteria(page, '1')
            elif re.search(third_level_pattern, page.pageObjects[0].text):
                self.Check_Criteria(page, '3')
            else:
                self.Check_Criteria(page, '2')

    def Check_Criteria(self, page, header_type):
        if page.pageObjects[0].data.alignment not in self.default_header_criteria[header_type]['alignment']:
            self.__check_results[page.header]['alignment'] = False
            self.output = False
        if page.pageObjects[0].data.paragraph_format.line_spacing \
                not in self.default_header_criteria[header_type]['line_spacing']:
            self.__check_results[page.header]['line_spacing'] = False
            self.output = False
        if round(page.pageObjects[0].data.paragraph_format.first_line_indent.cm, 2) \
                not in self.default_header_criteria[header_type]['first_line_indent']:
            self.__check_results[page.header]['first_line_indent'] = False
            self.output = False
        for elem in page.pageObjects[0].data.runs:
            if elem.bold not in self.default_header_criteria[header_type]['bold']:
                self.__check_results[page.header]['bold'] = False
                self.output = False
            if elem.italic not in self.default_header_criteria[header_type]['italic']:
                self.__check_results[page.header]['italic'] = False
                self.output = False
            if elem.underline not in self.default_header_criteria[header_type]['underline']:
                self.__check_results[page.header]['underline'] = False
                self.output = False
            if elem.font.size is not None \
                    and int(elem.font.size.pt) not in self.default_header_criteria[header_type]['font_size'] \
                    or elem.font.size is None and page.pageObjects[0].data.style.font.size.pt \
                    not in self.default_header_criteria[header_type]['font_size']:
                self.__check_results[page.header]['font_size'] = False
                self.output = False
            if elem.font.name is not None \
                    and elem.font.name not in self.default_header_criteria[header_type]['font_name'] \
                    or elem.font.name is None and page.pageObjects[0].data.style.font.name \
                    not in self.default_header_criteria[header_type]['font_name']:
                self.__check_results[page.header]['font_name'] = False
                self.output = False

    def ChangeMsg(self, msg):
        self.msg = msg

    def Get_output(self):
        for header, criteria in self.__check_results.items():
            is_correct = True
            for criterion, result in criteria.items():
                if not result:
                    if criterion == 'font_name':
                        self.ChangeMsg(f"{self.msg}Неверный  шрифрт в заголовке: {header}\n")
                        is_correct = False
                    elif criterion == 'font_size':
                        self.ChangeMsg(f"{self.msg}Неверный размер шрифта в заголовке: {header}\n")
                        is_correct = False
                    elif criterion == 'bold' or criterion == 'italic' or criterion == 'underline':
                        self.ChangeMsg(f"{self.msg}Неверный стиль шрифта в заголовке: {header}\n")
                        is_correct = False
                    elif criterion == 'alignment':
                        self.ChangeMsg(f"{self.msg}Неверное выравнивание в заголовке: {header}\n")
                        is_correct = False
                    elif criterion == 'first_line_indent':
                        self.ChangeMsg(f"{self.msg}Неверный отступ в заголовке: {header}\n")
                        is_correct = False
                    elif criterion == 'line_spacing':
                        self.ChangeMsg(f"{self.msg}Неверный межстрочный интервал в заголовке: {header}\n")
                        is_correct = False
            if is_correct:
                self.ChangeMsg(f"{self.msg}Заголовок \'{header}\' оформлен верно\n")

        return self.output

    def Get_check_result(self):
        return self.__check_results

    def Get_msg(self):
        return self.msg
    
