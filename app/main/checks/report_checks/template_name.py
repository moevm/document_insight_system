import re
from datetime import datetime


from ..base_check import BasePresCriterion, answer

CUR_YEAR = datetime.now().year


class ReportTemplateNameCheck(BasePresCriterion):
    label = "Проверка соответствия названия файла шаблону"
    description = f'Шаблон названия: "{CUR_YEAR}ВКР<номер_студ_билета>ФАМИЛИЯ", например "{CUR_YEAR}ВКР111111ИВАНОВ"'
    id = 'template_name'

    def __init__(self, file_info, regex=f"{CUR_YEAR}ВКР[0-9]{6}([А-ЯЁ]+)"):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.reg = regex

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла презентации "<i>{self.filename}</i>" не соответствует шаблону (Пример: {CUR_YEAR}ВКР030301ИВАНОВ)')
