import re
from datetime import datetime

from ..base_check import BasePresCriterion, answer

CUR_YEAR = datetime.now().year

TEMPLATE_TYPES = {
    'GFLab': f"Проверка соответствия названия файла шаблону: {CUR_YEAR}" + r"[0-9]{6}([А-ЯЁ]+)_ЛР[0-9]{1,2}" + f', например - "{CUR_YEAR}111111ИВАНОВ_ЛР1"',
    'VKR': f"Проверка соответствия названия файла шаблону: {CUR_YEAR}" + r"ВКР[0-9]{6}([А-ЯЁ]+)" + f', например - "{CUR_YEAR}ВКР111111ИВАНОВ"',
    None:  f"Проверка соответствия названия файла шаблону: {CUR_YEAR}" + r"ВКР[0-9]{6}([А-ЯЁ]+)" + f', например - "{CUR_YEAR}ВКР111111ИВАНОВ"'
}

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
            if pack and named_pack in pack:
                return TEMPLATE_TYPES[named_pack]
        return TEMPLATE_TYPES[None]
