import re
from datetime import datetime

from ..base_check import BasePresCriterion, answer

CUR_YEAR = datetime.now().year


class PresTemplateNameCheck(BasePresCriterion):
    label = "Проверка соответствия названия файла шаблону"
    description = 'Проверка соответствия названия файла шаблону: "<год>ВКР<номер_студ_билета>ФАМИЛИЯ_презентация", например - "2025ВКР111111ИВАНОВ_презентация"'
    id = 'template_name'

    def __init__(self, file_info, regex=f"{CUR_YEAR}"+"ВКР[0-9]{6}([А-ЯЁ]+)_(презентация|ПРЕЗЕНТАЦИЯ)"):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.reg = regex

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла презентации "<i>{self.filename}</i>" не соответствует шаблону. Допустимые форматы:<br>   2025ВКР111111ИВАНОВ_презентация')
