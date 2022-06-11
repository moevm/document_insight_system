import re

from app.main.checks.base_check import BaseCheck, answer
from app.utils.parse_for_html import format_header


class TemplateNameCheck(BaseCheck):
    def __init__(self, file, filename):
        super().__init__(file)
        self.filename = filename.split('.', 1)[0]
        self.reg = r"(\bПрезентация|\bПРЕЗЕНТАЦИЯ)_(ВКР|НИР)_(([А-ЯЁ][а-яё]+)|([А-ЯЁ]*))"

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False, f'Название файла презентации "<i>{self.filename}</i>" не соответствует шаблону. Допустимые форматы:<br>   Презентация_ВКР_Иванов<br>   ПРЕЗЕНТАЦИЯ_НИР_ИВАНОВ')
            
