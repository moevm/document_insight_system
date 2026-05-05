import re
from datetime import datetime

from ..base_check import BasePresCriterion, answer

CUR_YEAR = datetime.now().year

TEMPLATE_TYPES = {
    'GFLab': "Проверка соответствия названия файла шаблону: Отчет_ЛР[1-9]{1}(_[А-Я]{1}[а-яё]*)+, например - 'Отчет_ЛР1_Иванова_Петрова'",
    'CSLab': "Проверка соответствия названия файла шаблону ([номер_студ_билета][фамилия]_ОТЧЕТ_ЛР[номер_ЛР]): [0-9]{6}([А-ЯЁ]+)_ОТЧЕТ_ЛР[1-3]{1}, например - '534111ИВАНОВ_ОТЧЕТ_ЛР1'",
    'VKR': f"Проверка соответствия названия файла шаблону: {CUR_YEAR}" + r"ВКР[0-9]{6}([А-ЯЁ]+)" + f', например - "{CUR_YEAR}ВКР111111ИВАНОВ"'
}
DEFAULT_TEMPLATE_DESC = "Проверка соответствия названия файла требуемому шаблону."


class ReportTemplateNameCheck(BasePresCriterion):
    label = "Проверка соответствия названия файла шаблону"
    _description = ''
    id = 'template_name'

    def __init__(self, file_info, regex=f"{CUR_YEAR}" + r"ВКР[0-9]{6}([А-ЯЁ]+)"):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.reg = regex

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        return answer(False,
                        f'Название файла "<i>{self.filename}</i>" не соответствует шаблону: {self.reg}')

    @classmethod
    def description(cls, pack: str | None = None):
        if not pack:
            return TEMPLATE_TYPES[None]
        elif pack == 'ALL':
            return TEMPLATE_TYPES
        for named_pack in TEMPLATE_TYPES:
            if named_pack in pack:
                return TEMPLATE_TYPES[named_pack]
        return DEFAULT_TEMPLATE_DESC
