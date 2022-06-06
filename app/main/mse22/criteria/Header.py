import re
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Cm


class Header:
    msg = ''
    output = True
    __check_results = dict()
    default_header_criteria = {
        '1': {
            'font_name': ['Times New Roman'],
            'font_size': [14],
            'alignment': [WD_PARAGRAPH_ALIGNMENT.CENTER],
            'first_line_indent': [Cm(0)],
            'line_spacing': [Cm(1.5)],
            'bold': [True],
            'italic': [False, None],
            'underline': [False, None]
        },
        '2': {
            'font_name': ['Times New Roman'],
            'font_size': [14],
            'alignment': [WD_PARAGRAPH_ALIGNMENT.JUSTIFY],
            'first_line_indent': [Cm(1.25)],
            'line_spacing': [Cm(1.5)],
            'bold': [True],
            'italic': [False, None],
            'underline': [False, None]
        }
    }

    def __init__(self, page_objects):
        self.page_objects = page_objects

    def CheckHeader(self):
        application_pattern = r"(Приложение|ПРИЛОЖЕНИЕ|приложение) [А-ЯЁа-яё]"
        for page in self.page_objects:
            if page.header == 'Титульный лист':
                continue
            self.__check_results[page.header] = dict.fromkeys(self.default_header_criteria['1'].keys())
            if re.search(application_pattern, page.pageObjects[0].text):
                for criteria_name, criteria_value in self.default_header_criteria['1'].items():
                    self.Check_Criteria(page, criteria_name, criteria_value)
            else:
                for criteria_name, criteria_value in self.default_header_criteria['2'].items():
                    self.Check_Criteria(page, criteria_name, criteria_value)

    def Check_Criteria(self, page, criteria_name, criteria_value):
        if not hasattr(page.pageObjects[0].style_info, criteria_name):
            self.__check_results[page.header][criteria_name] = False
            self.output = False
        elif getattr(page.pageObjects[0].style_info, criteria_name) not in criteria_value:
            self.__check_results[page.header][criteria_name] = False
            self.output = False
        else:
            self.__check_results[page.header][criteria_name] = True

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
