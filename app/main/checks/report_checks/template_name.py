import re

from ..base_check import BasePresCriterion, answer


class TemplateNameCheck(BaseReportCriterion):
    description = "Проверка соответствия названия файла шаблону"
    id = 'template_name_report'
        # Шаблон: НОМЕР_ГРУППЫ_Фамилия_ИНИЦИАЛЫ_NIR2

    def __init__(self, file_info, regex="^\d+_[А-Яа-я]+\_[А-Я]{2}_NIR2$"):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.reg = regex

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла отчета "<i>{self.filename}</i>" не соответствует шаблону. Допустимый формат:<br>   1111_Иванов_ИИ_NIR2')
